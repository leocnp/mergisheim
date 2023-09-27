"""
Script to generate poetry conflicts to be resolved
"""

import subprocess
import uuid

from poetry_conflicts_generator import utils

REPOSITORY_NAME = "mergisheim"


gh_client = utils.get_github_client()


TEST_PACKAGES = [
    {"package": "PyYAML", "initial_version": "6.0.0", "version": "6.0.1"},
    {"package": "Jinja2", "initial_version": "3.0.0", "version": "3.1.0"},
]


def reset_packages():
    """Call before start to recreate the initial scenario"""
    print("*** Resetting packages versions in main branch origin")
    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["git", "pull"])

    # Set back the initial version of package
    for package, init_version in [
        (p["package"], p["initial_version"]) for p in TEST_PACKAGES
    ]:
        print(f"\t- try setting back {package} to {init_version}")
        subprocess.run(["poetry", "add", f"{package}={init_version}"])
    # Push cleaned to main
    subprocess.run(
        ["git", "commit", "-a", "-m", "'reset initial version of packages in main'"]
    )
    subprocess.run(["git", "push", "-u", "origin", "main"])


def main(clear_branches: bool = False):
    print("***### Start ###***\n")

    reset_packages()

    user = gh_client.get_user()
    repo = gh_client.get_repo(f"{user.login}/{REPOSITORY_NAME}")

    pr_uuid = str(uuid.uuid4()).split("-")[0]
    p1_head = f"{pr_uuid}-p1"
    p2_head = f"{pr_uuid}-p2"

    try:
        # 1. Create the dependency PRs
        # Create PR1 with first dependency updated (contains only the first one updated)
        utils.push_dependencies_update_branch(p1_head, [TEST_PACKAGES[0]])
        repo.create_pull(
            title=f"PR1({pr_uuid}): update first package",
            body=TEST_PACKAGES[0]["package"],
            base="main",
            head=p1_head,
        )

        # Create PR2 with second dependency updated (contains both updated)
        # must set back the package updated in p1 first
        # subprocess.run(
        #     [
        #         "poetry",
        #         "add",
        #         TEST_PACKAGES[0]["package"],
        #         TEST_PACKAGES[0]["initial_version"],
        #     ]
        # )
        utils.push_dependencies_update_branch(p2_head, TEST_PACKAGES)
        p2 = repo.create_pull(
            title=f"PR2({pr_uuid}): update second package",
            body=TEST_PACKAGES[-1]["package"],
            base="main",
            head=p2_head,
        )

        # 2. Merge PR2 -> PR1 should conflict on poetry files
        print("*** Merging PR2 creates a poetry conflict on PR1")
        # p2.merge()

    finally:
        # Clear branches at end
        if clear_branches:
            for branch in repo.get_branches():
                if not any(name in branch.name for name in ("main", p1_head, p2_head)):
                    print(f"*** Deleting outdated branch '{branch.name}'")
                    try:
                        # delete locally
                        subprocess.run(["git", "branch", "-d", branch.name])
                        # delete from origin
                        repo.get_git_ref(f"heads/{branch.name}").delete()  # refs/heads/
                        print("\t- deleted")
                    except Exception as e:
                        print(e)
                        continue

        # Back to main
        subprocess.run(["git", "checkout", "main"])


if __name__ == "__main__":
    main(clear_branches=True)


# 2. Create base PR
# p0_head_branch = f"{uuid}-p0-base"
# p0 = repo.create_pull(title=f"PR0({uid}): base", body="", base="main", head=p0_head_branch)
