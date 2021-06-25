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
        "limit", nargs="?", default="backuppc_clients",
        help="Limit execution to a pattern"
    )
    return parser.parse_args()

def main():
    options = parse_arguments()

    ansible_common.run_ansible_with_vault(
        [str(script_dir.parent / "backuppc_client_setup.yml"), "--limit", options.limit]
    )

if __name__ == "__main__":
    main()
