#!/usr/bin/env python3

import sys
import argparse
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "tools" / "lib"))
import ansible_common #pylint: disable=import-error,wrong-import-position

script_dir = pathlib.Path(__file__).resolve().parent

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Deployment tests for BackupPC clients"
    )
    parser.add_argument(
        "role", nargs="?",
        choices=["all", "backuppc-client", "backuppc-client-rsync", "win-backuppc-client"],
        default="all",
        help="Test selected role(s) only (default is 'all')"
    )
    parser.add_argument(
        "-l", "--limit",
        help="Limit execution to a pattern (used only when role parameter in not 'all')"
    )
    return parser.parse_args()

def run_test(role, limit):
    ansible_common.run(
        [
            "py.test", "-v", "--connection=ansible", "--sudo", f"{role}/tests",
            f"--hosts={limit}"
        ],
        cwd=str(script_dir.parents[1])
    )


def main():
    options = parse_arguments()

    role_list = {
        "backuppc-client": "backuppc_clients_linux",
        "backuppc-client-rsync": "backuppc_clients_rsync_linux",
        # "win-backuppc-client": "backuppc_clients_windows"
    }

    if options.role == "all":
        for role, limit in role_list.items():
            run_test(role, limit)
    else:
        run_test(options.role, options.limit)


if __name__ == "__main__":
    main()
