import subprocess

import github


CREATED_BRANCHES = []

def created_branch():
    pass


def get_github_client() -> github.Github:
    token = subprocess.run(["gh", "auth", "token"], capture_output=True)
    auth = github.Auth.Token(token.stdout.decode().strip())
    return github.Github(auth=auth)


def create_branch(repo, branch_name: str):
    # TODO?
    main = repo.get_branch(branch="main")
    base_commit = repo.get_commits(sha=main.commit.sha)[0]

    # branch = f"{base_branch_name}-{str(uuid.uuid4())}"
    repo.create_git_ref(f"refs/heads/{branch_name}", base_commit.sha)  # create branch
    return branch_name


def _create_local_branch(name: str):
    subprocess.run(["git", "checkout", "-b", name])


def push_dependencies_update_branch(head: str, package: str, version: str):
    print(f"- Create head branch {head} with poetry package {package}={version}")
    _create_local_branch(head)
    # poetry update
    subprocess.run(["poetry", "add", f"{package}={version}"])
    # commit
    subprocess.run(["git", "commit", "-a", "-m", f"'dependency update {package}={version}'"])
    # push to upstream
    subprocess.run(["git", "push", "-u", "origin", head])


# def create_pull(repo, body: str, base: str, head: str):
#     pass
