#!/usr/bin/env python3

import sys
import os
import argparse
import pathlib
import json
import subprocess
import humanfriendly.prompts

sys.path.append(str(pathlib.Path(__file__).resolve().parent / "lib"))
import ansible_common #pylint: disable=import-error,wrong-import-position

script_dir = pathlib.Path(__file__).resolve().parent

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run a role from current repository"
    )
    parser.add_argument(
        "role_name", nargs="?", help="Role name"
    )
    parser.add_argument(
        "limit", nargs="?", help="Limit execution to a pattern"
    )
    parser.add_argument(
        "-e", "--extra-vars", action="append", help="Set additional variables"
    )
    parser.add_argument(
        "-r", "--roles-dir", help="Roles directory", default=str(script_dir.parent)
    )
    parser.add_argument(
        "-f", "--force", action="store_true", default=False,
        help=(
            "Continue execution even if local repository is not up to date "
            "with the upstream"
        )
    )
    return parser.parse_args()

def select_role(roles_dir, last_used_role):
    roles = []
    for subdir in pathlib.Path(roles_dir).iterdir():
        if subdir.is_dir() and (subdir / "tasks/main.yml").exists():
            roles += [subdir.name]

    selection = humanfriendly.prompts.prompt_for_choice(
        sorted(roles) + ["Exit"],
        default=last_used_role
    )
    if selection == "Exit":
        sys.exit("Cancelled by user")
    return selection

def select_subset(last_used_subset):
    inventory = json.loads(
        subprocess.check_output(["ansible-inventory", "--list"])
    )
    # [!] groups is a set, not a list, it will have unique items
    groups = set()
    for group in inventory["all"]["children"]:
        if group != "ungrouped":
            groups.add(group)
    hosts = set()
    for group in inventory:
        if group not in ("_meta", "all"):
            if inventory[group].get("hosts", None):
                for host in inventory[group]["hosts"]:
                    hosts.add(host)
    # host_and_groups = ["all"] + list(sorted(groups)) + list(sorted(hosts))
    selection = humanfriendly.prompts.prompt_for_choice(
        ["all"] + list(sorted(groups)) + list(sorted(hosts)) + ["Exit"],
        default=last_used_subset
    )
    if selection == "Exit":
        sys.exit("Cancelled by user")
    return selection
    # print(host_and_groups)


def main():
    options = parse_arguments()

    ansible_common.check_repo_is_up_to_date(force=options.force)

    config_file_name = os.path.expanduser("~/.cache/cheretbe/ansible-playbooks/run_role_cfg.json")
    if os.path.isfile(config_file_name):
        with open(config_file_name) as config_f:
            config = json.load(config_f)
    else:
        config = {}

    if options.role_name is None:
        options.role_name = select_role(
            roles_dir=options.roles_dir,
            last_used_role=config.get("last_used_role", None)
        )
    config["last_used_role"] = options.role_name

    if not options.limit:
        options.limit = select_subset(
            last_used_subset=config.get("last_used_subset", None)
        )
    config["last_used_subset"] = options.limit

    os.makedirs(os.path.dirname(config_file_name), exist_ok=True)
    with open(config_file_name, "w", encoding="utf-8") as config_f:
        json.dump(config, config_f, ensure_ascii=False, indent=4)

    additional_params = ["--extra-vars", f"role_name={options.role_name}"]
    if options.extra_vars:
        for extra_var in options.extra_vars:
            additional_params += ["--extra-vars", extra_var]
    if options.limit:
        additional_params += ["--limit", options.limit]

    ansible_common.run(
        [
            "ansible-playbook",
            os.path.join(options.roles_dir, "run_role.yml"),
        ] + additional_params
    )

if __name__ == "__main__":
    main()
