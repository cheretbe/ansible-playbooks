#!/usr/bin/env python3

import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Helper utility to run testinfra tests")
    parser.add_argument(
        "test_dir",
        help="Run tests, located in a specified directory"
    )
    parser.add_argument(
        "-n", "--host-name",
        default=None,
        help="Host name to run tests against"
    )
    parser.add_argument(
        "-b", "--backend",
        default="docker",
        help="Connection backend to use (default: docker)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Increase verbosity"
    )
    parser.add_argument(
        "-s", "--no_capture",
        action="store_true",
        default=False,
        help="Use '--capture=no' (-s) as pytest's capture method"
    )
    options = parser.parse_args()

    pytest_cmd = "pytest " + options.test_dir

    # Fix ansible/testinfra driver name mismatch
    if options.backend == "lxd":
        options.backend = "lxc"
    if options.host_name:
        pytest_cmd += f" --hosts={options.backend}://{options.host_name}"
    if options.verbose:
        pytest_cmd += " -v"
    if options.no_capture:
        pytest_cmd += " -s"

    print(pytest_cmd, flush=True)
    subprocess.check_call(pytest_cmd, shell=True)

if __name__ == "__main__":
    main()
