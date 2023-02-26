#!/usr/bin/env python3

import sys
import traceback
import argparse
import datetime
import subprocess


def print_exception(exc, verbose):
    print(f"[!] ERROR: {str(exc)}", file=sys.stderr, flush=True)
    if verbose:
        print(traceback.format_exc(), file=sys.stderr, flush=True)


def main(args):
    restart_needed = False
    # We expect tab-delimited output like this:
    # aX/6OY9B4tYjvCCsLnRt5ejtluayl/E2MMGhkhYALw4=  1677237195
    try:
        latest_hs_timestamp = int(
            subprocess.check_output(
                ("wg", "show", args.wg_profile, "latest-handshakes"), text=True
            )
            .rstrip()
            .split("\t")[1]
        )
        latest_hs_delta = (
            int(round(datetime.datetime.now().timestamp())) - latest_hs_timestamp
        )
        if args.verbose:
            latest_hs = datetime.datetime.fromtimestamp(latest_hs_timestamp)
            print(
                f"Latest handshake: {latest_hs_delta}s ago at {latest_hs} ({latest_hs_timestamp})",
                flush=True,
            )
        # By default handshakes happen every two minutes
        if latest_hs_delta > args.timeout:
            print(
                f"Latest handshake age of {latest_hs_delta}s is over "
                f"the threshold of {args.timeout}s",
                flush=True,
            )
            restart_needed = True
    # This script is intended to run as systemd timer unit and we do want to catch
    # everything so that system log is not spammed with long stack traces
    except Exception as exc:  # pylint: disable=broad-except
        print_exception(exc, args.verbose)
        restart_needed = True
    if restart_needed:
        print(f"Restarting 'wg-quick@{args.wg_profile}' service", flush=True)
        try:
            subprocess.check_call(
                ("systemctl", "restart", f"wg-quick@{args.wg_profile}.service")
            )
        except Exception as exc:  # pylint: disable=broad-except
            print_exception(exc, args.verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wg_profile", help="Wireguard profile name")
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Increase verbosity"
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=240,
        help="Max handshake age in seconds (default=240)",
    )

    parsed_args = parser.parse_args()

    main(parsed_args)
