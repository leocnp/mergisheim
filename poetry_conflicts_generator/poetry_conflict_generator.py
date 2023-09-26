"""
Script to generate poetry conflicts to be resolved
"""

import uuid
import github
import subprocess

from poetry_conflicts_generator import utils


REPOSITORY_NAME = "mergisheim"


gh_client = utils.get_github_client()


def reset_packages():
    """Call before start to recreate the initial scenario"""
    # TODO
    pass


def main():
    # 1. reset state of packages to recreate scneario
    # 2. create the first branch
    # PyYAML=6.0.0

    reset_packages()

    user = gh_client.get_user()
    repo = gh_client.get_repo(f"{user.login}/{REPOSITORY_NAME}")

    uid = str(uuid.uuid4()).split("-")[0]

    # Create base PR
    p0_head_branch = f"{uuid}-p0-base"
    p0 = repo.create_pull(title=f"PR0({uid}): base", body="", base="main", head=p0_head_branch)

    # Create PR1 with first dependency updated
    p1 = repo.create_pull(title=f"PR1({uid}): update dependency ", body="", base=p0_head_branch, head=f"{uuid}-p1")

    # Create PR2 with first dependency updated
    # p2 = repo.create_pull(title=f"PR2({uid}): update dependency ", body="", base=p0_head_branch, head=f"{uuid}-p1")

    # Checkout PR1 and push an update


if __name__ == "__main__":
    # main()
    utils.create_local_branch("testbranch")
