import os
import sys
import subprocess
import pathlib
import colorama

script_dir = pathlib.Path(__file__).resolve().parent

colorama.init()

def color_print(fore_color, msg):
    print(f"{fore_color}{msg}{colorama.Style.RESET_ALL}")

def run(cmd_args, echo=True, **kwargs):
    if echo:
        print(cmd_args)
    subprocess.check_call(cmd_args, **kwargs)

def run_ansible_with_vault(ansible_args):
    ansible_cmd = ["ansible-playbook"]

    if "ANSIBLE_VAULT_PASSWORD" in os.environ:
        print("Using ANSIBLE_VAULT_PASSWORD environment variable as a vault password")
        ansible_cmd += [
            "--vault-password-file",
            str(script_dir / "ansible_vault_env_pass_file.sh")
        ]
    else:
        color_print(
            colorama.Fore.CYAN + colorama.Style.BRIGHT,
            "Hint: consider setting ANSIBLE_VAULT_PASSWORD environment variable"
        )
        ansible_cmd += ["--ask-vault-password"]

    run(ansible_cmd + ansible_args)

def check_repo_is_up_to_date(repo_path=None, force=False):
    if not repo_path:
        repo_path = script_dir.parents[1]

    print(f"Checking if '{repo_path}' repo is up to date")
    subprocess.check_call(["git", "fetch", "--quiet"], cwd=repo_path)
    # @{u} is short for @{upstream} (documented in git rev-parse --help)
    latest_upstream_hash = subprocess.check_output(
        ["git", "rev-list", "-n", "1", "@{u}"], cwd=repo_path
    )
    latest_local_hash = subprocess.check_output(
        ["git", "rev-list", "-n", "1", "@"], cwd=repo_path
    )
    if not latest_upstream_hash == latest_local_hash:
        if force:
            color_print(
                colorama.Fore.CYAN + colorama.Style.BRIGHT,
                f"{repo_path}: local branch is not up to date with the upstream. " +
                "Consider calling 'git pull'"
            )
        else:
            sys.exit(
                f"{repo_path}: local branch is not up to date with the upstream. " +
                "Call 'git pull' or use --force option"
            )
