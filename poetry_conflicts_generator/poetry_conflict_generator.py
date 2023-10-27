"""
Script to generate poetry conflicts to be resolved
"""

import subprocess
import uuid

from poetry_conflicts_generator import utils

REPOSITORY_NAME = "mergisheim"

CREATE_FROM_FORK: bool = True

if CREATE_FROM_FORK:
    # fork configured on lecrepont02 - see `git remote -v`
    from secrets import token
    # ORIGIN = "fork"
    ORIGIN = f"https://{token}@github.com/lecrepont02/mergisheim.git"
else:
    ORIGIN = "origin"


gh_client = utils.get_github_client(from_fork=CREATE_FROM_FORK)


TEST_PACKAGES = [
    {"package": "PyYAML", "initial_version": "6.0.0", "version": "6.0.1"},
    {"package": "Jinja2", "initial_version": "3.1.0", "version": "3.1.2"},
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
        if init_version is None:
            # Removes a package
            subprocess.run(["poetry", "remove", package])
        else:
            # subprocess.run(["poetry", "add", f"{package}={init_version}"])
            # Adds as caret requirement
            subprocess.run(["poetry", "add", f"{package}@^{init_version}"])

    # Push cleaned to main
    subprocess.run(
        ["git", "commit", "-a", "-m", "'reset initial version of packages in main'"]
    )

    subprocess.run(["git", "push", "-u", "origin"])  #  origin, "main"])

    if CREATE_FROM_FORK:
        # sync the fork
        print("Sync the fork repo")


def main(clear_branches: bool = False):
    print(f"*** Running conflicts in a PR on forked repository? {CREATE_FROM_FORK} ***")

    # Recreate initial scenario
    reset_packages()

    user = gh_client.get_user()
    print(f"*** Getting repo {user.login}/{REPOSITORY_NAME} ***")
    # repo = gh_client.get_repo(f"{user.login}/{REPOSITORY_NAME}")
    # Actually PR is created on the main repo not the forked one !
    repo = gh_client.get_repo(f"lecrepont01/{REPOSITORY_NAME}")

    pr_uuid = str(uuid.uuid4()).split("-")[0]
    p2_head = f"{pr_uuid}-p2"
    p1_head = f"{pr_uuid}-p1"

    try:
        # Create the dependency PRs
        if CREATE_FROM_FORK:
            # for API specify the forked head user
            p1_head_api = f"{user.login}:{p1_head}"
            p2_head_api = f"{user.login}:{p2_head}"
        else:
            p1_head_api = p1_head
            p2_head_api = p2_head

        # 1. Create PR1 with an updated dependency
        utils.push_dependencies_update_branch(ORIGIN, p1_head, [TEST_PACKAGES[0]])
        p1 = repo.create_pull(
            title=f"PR1({pr_uuid}): add first package update",
            body=TEST_PACKAGES[0]["package"],
            base="main",
            head=p1_head_api,
        )
        print("Created p1")

        # 2. Create PR2 with an added dependency in the meantime
        # must set back the package updated in p1 first
        # subprocess.run(
        #     [
        #         "poetry",
        #         "add",
        #         TEST_PACKAGES[0]["package"],
        #         TEST_PACKAGES[0]["initial_version"],
        #     ]
        # )
        utils.push_dependencies_update_branch(ORIGIN, p2_head, [TEST_PACKAGES[1]])
        p2 = repo.create_pull(
            title=f"PR2({pr_uuid}): add second package update",
            body=TEST_PACKAGES[-1]["package"],
            base="main",
            head=p2_head_api,
        )
        print(p2)

        # 2. Merge PR1 with update -> PR2 conflicts on the lock file
        print("*** Merging PR1 creates a poetry conflict on PR1")
        p1.merge()

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
    print("***### Start ###***\n")
    main(clear_branches=True)
    # try:
    #     print("*** Pre-condition: git login ***")
    # finally:


# 2. Create base PR
# p0_head_branch = f"{uuid}-p0-base"
# p0 = repo.create_pull(title=f"PR0({uid}): base", body="", base="main", head=p0_head_branch)
