#!/usr/bin/env python3

import sys
import os
import argparse
import pathlib
import json
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
        "-l", "--limit", help="Limit execution to a pattern"
    )
    parser.add_argument(
        "-e", "--extra-vars", help="Set additional variables"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", default=False,
        help=(
            "Continue execution even if local repository is not up to date "
            "with the upstream"
        )
    )
    return parser.parse_args()

def select_role(last_used_role):
    roles = []
    for subdir in script_dir.parent.iterdir():
        if subdir.is_dir() and (subdir / "tasks/main.yml").exists():
            roles += [subdir.name]

    selection = humanfriendly.prompts.prompt_for_choice(
        sorted(roles) + ["Exit"],
        default=last_used_role
    )
    if selection == "Exit":
        sys.exit("Cancelled by user")


    return selection

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
        options.role_name = select_role(config.get("last_used_role", None))
    config["last_used_role"] = options.role_name

    os.makedirs(os.path.dirname(config_file_name), exist_ok=True)
    with open(config_file_name, "w", encoding="utf-8") as config_f:
        json.dump(config, config_f, ensure_ascii=False, indent=4)


    # print(f"options.role_name: {options.role_name}")
    additional_params = ["--extra-vars", f"role_name={options.role_name}"]
    if options.extra_vars:
        additional_params += ["--extra-vars", options.extra_vars]
    if options.limit:
        additional_params += ["--limit", options.limit]

    ansible_common.run(
        [
            "ansible-playbook",
            str(script_dir.parent / "run_role.yml"),
        ] + additional_params
    )

if __name__ == "__main__":
    main()
