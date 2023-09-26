"""
Script to generate poetry conflicts to be resolved
"""

import uuid
import github
import subprocess

from poetry_conflicts_generator import utils


REPOSITORY_NAME = "mergisheim"


gh_client = utils.get_github_client()


TEST_PACKAGES = {
    "PyYAML": "6.0.0",
    "Jinja2": "3.1.0"
}


def reset_packages():
    """Call before start to recreate the initial scenario"""
    print("- Resetting packages in base")
    # Remove previously installed package if merged (poetry remove)
    for package in TEST_PACKAGES:
        subprocess.run(["poetry", "remove", package])
    # Push back to main the initial state
    pass


def main(clear_branches: bool = False):
    print("*** Start ***")
    # 1. reset state of packages to recreate scneario
    reset_packages()

    user = gh_client.get_user()
    repo = gh_client.get_repo(f"{user.login}/{REPOSITORY_NAME}")
    uid = str(uuid.uuid4()).split("-")[0]

    # 2. Create base PR
    # p0_head_branch = f"{uuid}-p0-base"
    # p0 = repo.create_pull(title=f"PR0({uid}): base", body="", base="main", head=p0_head_branch)

    # 3. Create the dependency PRs
    # Create PR1 with first dependency updated
    p1_head = f"{uid}-p1"
    utils.push_dependencies_update_branch(p1_head, "PyYAML", "6.0.0")
    p1 = repo.create_pull(title=f"PR1({uid}): update dependency ", body="PyYAML - 6.0.0", base="main", head=p1_head)
    print(p1)

    # Create PR2 with second dependency updated
    p2_head = f"{uid}-p2"
    print(p2_head)
    # p2 = repo.create_pull(title=f"PR2({uid}): update dependency ", body="", base=p0_head_branch, head=f"{uuid}-p1")

    # 4. Merge PR1 -> PR2 should conflict

    # Clear branches at end
    if clear_branches:
        for branch in repo.get_branches():
            if "main" not in branch.name:
                print(f"- Deleting branch {branch.name}")
                try:
                    repo.get_git_ref(f"refs/heads/{branch.name}").delete()
                except Exception as e:
                    print(e)
                    continue


if __name__ == "__main__":
    main()
