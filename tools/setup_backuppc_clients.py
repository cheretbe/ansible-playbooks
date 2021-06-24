#!/usr/bin/env python3

import sys
import argparse
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parent / "lib"))
import ansible_common #pylint: disable=import-error,wrong-import-position

script_dir = pathlib.Path(__file__).resolve().parent

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Setup BackupPC clients"
    )
    parser.add_argument(
        "-l", "--linux-hosts", default="backuppc_clients_linux",
        help="Linux hosts: limit execution to a pattern (default: backuppc_clients_linux)"
    )
    parser.add_argument(
        "-w", "--windows-hosts", default="backuppc_clients_windows",
        help="Windows hosts: limit execution to a pattern (default: backuppc_clients_windows)"
    )
    return parser.parse_args()

def main():
    options = parse_arguments()

    ansible_common.run_ansible_with_vault(
        [str(script_dir.parent / "run_role.yml"),
        "--extra-vars", "role_name=backuppc-client",
        "--limit", options.linux_hosts]
    )
    ansible_common.run_ansible_with_vault(
        [str(script_dir.parent / "run_role.yml"),
        "--extra-vars", "role_name=win-backuppc-client",
        "--limit", options.windows_hosts]
    )

if __name__ == "__main__":
    main()
