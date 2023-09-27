"""
Script to generate poetry conflicts to be resolved
"""

import subprocess
import uuid

from poetry_conflicts_generator import utils

REPOSITORY_NAME = "mergisheim"


gh_client = utils.get_github_client()


TEST_PACKAGES = [
    {"package": "PyYAML", "version": "6.0.0"},
    {"package": "Jinja2", "version": "3.1.0"},
]


def reset_packages():
    """Call before start to recreate the initial scenario"""
    print("*** Resetting packages in base")
    # Remove previously installed package if merged (poetry remove)
    for package in [p["package"] for p in TEST_PACKAGES]:
        subprocess.run(["poetry", "remove", package])


def main(clear_branches: bool = False):
    print("***### Start ###***")
    # 1. reset state of packages to recreate the scenario
    reset_packages()

    user = gh_client.get_user()
    repo = gh_client.get_repo(f"{user.login}/{REPOSITORY_NAME}")
    uid = str(uuid.uuid4()).split("-")[0]

    # 3. Create the dependency PRs
    # Create PR1 with first dependency updated
    p1_head = f"{uuid}-p1"
    utils.push_dependencies_update_branch(
        p1_head, TEST_PACKAGES[0]["package"], TEST_PACKAGES[0]["version"]
    )
    p1 = repo.create_pull(
        title=f"PR1({uid}): update first package",
        body=TEST_PACKAGES[0]["package"],
        base="main",
        head=p1_head,
    )
    print(p1)

    # Create PR2 with second dependency updated
    p2_head = f"{uuid}-p2"
    utils.push_dependencies_update_branch(
        p2_head, TEST_PACKAGES[-1]["package"], TEST_PACKAGES[-1]["version"]
    )
    # must remove the package update in p1 first
    subprocess.run(["poetry", "remove", TEST_PACKAGES[0]["version"]])
    p2 = repo.create_pull(
        title=f"PR2({uid}): update second package",
        body=TEST_PACKAGES[-1]["package"],
        base="main",
        head=p2_head,
    )
    print(p2)

    # 4. Merge PR2 -> PR1 should conflict
    print("*** Mering PR2 creates a poetry conflict on PR1")

    # Clear branches at end
    if clear_branches:
        for branch in repo.get_branches():
            if "main" not in branch.name:
                print(f"*** Deleting branch {branch.name}")
                try:
                    repo.get_git_ref(f"refs/heads/{branch.name}").delete()
                except Exception as e:
                    print(e)
                    continue

    # switch back to main
    subprocess.run(["git", "checkout", "main"])


if __name__ == "__main__":
    main()


# 2. Create base PR
# p0_head_branch = f"{uuid}-p0-base"
# p0 = repo.create_pull(title=f"PR0({uid}): base", body="", base="main", head=p0_head_branch)
