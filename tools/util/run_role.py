#!/usr/bin/env python3

import sys
import pathlib
import subprocess
import PyInquirer
import ansible.constants
import ansible.inventory.manager
import ansible.parsing.dataloader

def get_target():
    inventory = ansible.inventory.manager.InventoryManager(
        loader=ansible.parsing.dataloader.DataLoader(),
        # Somehow DEFAULT_HOST_LIST is there ¯\_( ツ )_/¯
        sources=ansible.constants.DEFAULT_HOST_LIST # pylint: disable=no-member
    )
    inv_groups = sorted(inventory.list_groups(), key=str.casefold)
    inv_hosts = sorted([str(host) for host  in inventory.list_hosts()], key=str.casefold)
    if len(inv_hosts) == 0:
        sys.exit("ERROR: Host list is empty")

    choices = [PyInquirer.Separator("==== Groups ====")]
    choices.extend([{"name": f"  [{group}]", "value": group} for group in inv_groups])

    if len(inv_hosts) > 1:
        choices.append(PyInquirer.Separator("==== Hosts ===="))
        choices.extend([{"name": f"  {host}", "value": host} for host in inv_hosts])

    answers = PyInquirer.prompt([
        {
            "type": "list",
            "name": "selection",
            "message": "Select a group or a host (Ctrl+C to cancel)",
            # Doesn't work for now. See https://github.com/CITGuru/PyInquirer/issues/17
            # and https://github.com/CITGuru/PyInquirer/issues/90
            # "default": 2,
            "choices": choices
        }
    ])
    if not answers:
        sys.exit(1)
    return answers["selection"]

def get_role():
    # ../..
    roles_dir = pathlib.Path(__file__).resolve().parents[2]
    roles = []
    for child_obj in roles_dir.iterdir():
        if child_obj.is_dir():
            if (child_obj / "tasks" / "main.yml").exists():
                roles.append(child_obj.name)
    roles.sort()

    answers = PyInquirer.prompt([
        {
            "type": "list",
            "name": "selection",
            "message": "Select a role to run (Ctrl+C to cancel)",
            # Doesn't work for now. See https://github.com/CITGuru/PyInquirer/issues/17
            # and https://github.com/CITGuru/PyInquirer/issues/90
            # "default": 2,
            "choices": roles
        }
    ])
    if not answers:
        sys.exit(1)
    return str(roles_dir / answers["selection"])


def main():
    target = get_target()
    role = get_role()
    subprocess.check_call([
        "ansible-playbook", "run_role.yml", "-l", target, "--extra-vars",
        f'role_name={role}',
        "--private-key", "/home/npa/keys/npa_openssh.key", "--ask-become-pass"
    ])


if __name__ == "__main__":
    main()
