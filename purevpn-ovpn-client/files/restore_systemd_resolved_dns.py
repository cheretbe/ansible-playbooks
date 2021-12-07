#!/usr/bin/python3

import sys
import os
import subprocess

# This script is a cleanup counterpart of update_resolve_conf.py
# It is also intended to be run as ExecStartPre entry for OpenVPN client
# unit file and makes sure DNS settings are correct even if the service
# crashed and /etc/resolv.conf contains unreachable nameserver entries

needs_restore = False
if not os.path.islink("/etc/resolv.conf"):
    needs_restore = True
elif os.readlink("/etc/resolv.conf") != "/run/systemd/resolve/resolv.conf":
    needs_restore = True

if needs_restore:
    print("Restoring /etc/resolv.conf as a link to /run/systemd/resolve/resolv.conf", flush=True)
    os.unlink("/etc/resolv.conf")
    os.symlink("/run/systemd/resolve/resolv.conf", "/etc/resolv.conf")
    # degraded (the system is operational but one or more units failed) returns
    # non-zero exit code, for that reason we ignore the exit code and analyze
    # text output
    # https://www.freedesktop.org/software/systemd/man/systemctl.html#is-system-running
    if subprocess.run( # pylint: disable=subprocess-run-check
            ["/usr/bin/systemctl", "is-system-running"],
            capture_output=True
    ).stdout.decode().strip() in ["running", "degraded"]:
        # When /etc/resolv.conf is not symlinked to /run/systemd/resolve/resolv.conf,
        # systemd-resolved parses /etc/resolv.conf contents and uses nameserver entries.
        # We restart it to make sure it doesn't pick up our nameservers, that are
        # going to become unreachable
        print("Restarting systemd-resolved service", flush=True)
        subprocess.check_call(
            ["/usr/bin/systemctl", "restart", "systemd-resolved.service"]
        )
        sys.stdout.flush()
