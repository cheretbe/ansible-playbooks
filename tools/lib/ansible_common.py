import os
import subprocess
import pathlib
import colorama

script_dir = pathlib.Path(__file__).resolve().parent

colorama.init()

def color_print(fore_color, msg):
    # print("{color}{msg}{reset}".format(color=fore_color, msg=msg, reset=colorama.Style.RESET_ALL))
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
