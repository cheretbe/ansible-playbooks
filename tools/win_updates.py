#!/usr/bin/env python3

import sys
import argparse
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parent / "lib"))
import ansible_common #pylint: disable=import-error,wrong-import-position

script_dir = pathlib.Path(__file__).resolve().parent

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Install updates on Windows clients"
    )
    parser.add_argument(
        "limit", help="Limit execution to a pattern"
    )
    parser.add_argument(
        "-r", "--reboot", action="store_true", default=False,
        help=(
            "Allow automatic reboots if it is required and continue to install "
            "updates after the reboot"
        )
    )
    return parser.parse_args()

def main():
    options = parse_arguments()

    extra_vars = []
    if options.reboot:
        extra_vars = ["--extra-vars", "win_updates_allow_reboot=yes"]

    ansible_common.run(
        [
            "ansible-playbook",
            str(script_dir.parent / "win_updates.yml"),
            "--limit", options.limit
        ] + extra_vars
    )

if __name__ == "__main__":
    main()
