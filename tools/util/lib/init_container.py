import sys
import os
import json
import subprocess
import pathlib
import ansible.inventory.manager
import ansible.parsing.dataloader
import PyInquirer
import common

def get_lxd_host_name():
    loader = ansible.parsing.dataloader.DataLoader()
    inventory = ansible.inventory.manager.InventoryManager(
        loader=loader,
        # Somehow DEFAULT_HOST_LIST is there ¯\_( ツ )_/¯
        sources=ansible.constants.DEFAULT_HOST_LIST # pylint: disable=no-member
    )
    inv_hosts = sorted([str(i) for i in inventory.get_hosts()])
    if len(inv_hosts) == 0:
        sys.exit("ERROR: Ansible inventory host list is empty")

    answers = PyInquirer.prompt([
        {
            "type": "list",
            "name": "selection",
            "message": "Select Ansible-managed LXD host (Ctrl+C to cancel)",
            # Doesn't work for now. See https://github.com/CITGuru/PyInquirer/issues/17
            # and https://github.com/CITGuru/PyInquirer/issues/90
            # "default": 2,
            "choices": inv_hosts
        }
    ])
    if not answers:
        sys.exit(1)

    return answers["selection"]


def main():

    host_name = get_lxd_host_name()

    print(f"Getting container list from '{host_name}'")
    lxc_output = json.loads(subprocess.check_output(
        ["ansible", host_name, "--become", "-a", "lxc list --format csv"],
        env={
            "ANSIBLE_LOAD_CALLBACK_PLUGINS": "true",
            "ANSIBLE_STDOUT_CALLBACK": "json"
        }
    ))
    container_names = [
        i.split(",")[0] for i in lxc_output["plays"][0]["tasks"][0]["hosts"]
            [host_name]["stdout_lines"]
    ]
    if len(container_names) == 0:
        sys.exit(f"ERROR: LXD container list on '{host_name}' is empty")
    elif len(container_names) == 1:
        container_name = container_names[0]
        print(f"Auto-selecting the only LXD container '{container_name}'")
    else:
        container_name = common.select_from_list("Select a container", container_names)

    # [!] The config is shared with init_linux_host.py
    config_file_name = os.path.expanduser("~/.cache/cheretbe/ansible-utils/host_init_cfg.json")
    if os.path.isfile(config_file_name):
        with open(config_file_name) as conf_f:
            config = json.load(conf_f)
    else:
        config = {}

    config["ansible_user"] = common.read_input("Ansible user name", config.get("ansible_user"))
    config["ansible_public_key"] = common.read_input(
        "Ansible user public key file", config.get("ansible_public_key")
    )

    os.makedirs(os.path.dirname(config_file_name), exist_ok=True)
    with open(config_file_name, "w", encoding="utf-8") as conf_f:
        json.dump(config, conf_f, ensure_ascii=False, indent=4)

    print("Running playbook 'init_container.yml'")
    subprocess.check_call([
        "ansible-playbook", "-l", host_name, "--become",
        pathlib.Path(__file__).resolve().parent / "init_container.yml",
        "--extra-vars", f"init_container_name={container_name}",
        "--extra-vars", f"init_container_key_file={config['ansible_public_key']}",
        "--extra-vars", f"init_container_ansible_user={config['ansible_user']}"
    ])


if __name__ == "__main__":
    main()
