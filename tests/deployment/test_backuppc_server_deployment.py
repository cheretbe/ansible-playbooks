#!/usr/bin/env python3

import os
import sys
import argparse
import pathlib
import subprocess
import colorama

parser = argparse.ArgumentParser()
parser.add_argument("hosts", nargs="?", default="", help="Host list")
parser.add_argument("-u", "--www-user-name", dest="www_user", default=None,
    help="User name for status page http request")
options = parser.parse_args()

project_root = str(pathlib.Path(__file__).resolve().parents[2])
testinfra_cmd = ["py.test", "-v", "--connection=ansible", "backuppc-server/tests"]
if options.hosts:
    testinfra_cmd += [f"--hosts={options.hosts}"]
if options.www_user:
    testinfra_cmd += [f"--www-user={options.www_user}"]
testinfra_cmd_to_print = testinfra_cmd.copy()
if "AO_BACKUPPC_TEST_PASSWORD" in os.environ:
    testinfra_cmd += [f"--www-password={os.environ['AO_BACKUPPC_TEST_PASSWORD']}"]
    testinfra_cmd_to_print += ["--www-password=*****"]
else:
    print(
        colorama.Fore.YELLOW + colorama.Style.BRIGHT +
        "[!] WARNING: AO_BACKUPPC_TEST_PASSWORD environment variable is not defined" +
        colorama.Style.RESET_ALL
    )

print(testinfra_cmd_to_print)
rc = subprocess.call(
    testinfra_cmd,
    cwd=project_root
)
if rc !=0:
    sys.exit(f"Command {testinfra_cmd_to_print} returned non-zero exit status {rc}")
