import subprocess

import github


def get_github_client(from_fork: bool = False) -> github.Github:
    if from_fork:
        # fetch token from the secret yaml file for lecrepont02
        from secrets import token
    else:
        # fetch from gh cli
        token = subprocess.run(["gh", "auth", "token"], capture_output=True)
        token = token.stdout.decode().strip()
    auth = github.Auth.Token(token)
    return github.Github(auth=auth)


def _create_local_branch(name: str):
    # from main
    subprocess.run(["git", "checkout", "-b", name, "main"])


def push_dependencies_update_branch(origin: str, head: str, packages: list[dict]):
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
    subprocess.run(["git", "push", "-u", origin, head])
