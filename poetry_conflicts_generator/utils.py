import subprocess

import github


def get_github_client() -> github.Github:
    token = subprocess.run(["gh", "auth", "token"], capture_output=True)
    auth = github.Auth.Token(token.stdout.decode().strip())
    return github.Github(auth=auth)


def _create_local_branch(name: str):
    # from main
    subprocess.run(["git", "checkout", "-b", name, "main"])


def push_dependencies_update_branch(head: str, packages: list[dict]):
    print(f"*** Create head branch '{head}' with poetry package(s) {packages}")

    _create_local_branch(head)
    for p in packages:
        package = p["package"]
        version = p["version"]

        print(f"\t- package {package}=@^{version}")
        # # rebase from main first
        # subprocess.run(["git", "rebase", "main"])
        # poetry update
        subprocess.run(["poetry", "add", f"{package}@^{version}"])
    # commit
    subprocess.run(
        ["git", "commit", "-a", "-m", f"'dependency update {packages[-1]['package']}'"]
    )
    # push to upstream
    subprocess.run(["git", "push", "-u", "origin", head])
