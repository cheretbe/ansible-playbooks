import os
import subprocess
import tempfile
import threading
import pathlib

script_dir = pathlib.Path(__file__).resolve().parent

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
        ansible_cmd += ["--ask-vault-password"]

    run(ansible_cmd + ansible_args)
