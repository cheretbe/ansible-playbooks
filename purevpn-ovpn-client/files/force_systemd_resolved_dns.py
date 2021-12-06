#!/usr/bin/python3

import sys
import os
import subprocess

# Refer to update_resolve_conf.py to see comments and general logic
# This script is intended to be run as ExecStartPre entry for OpenVPN client
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
    print("Restarting systemd-resolved service", flush=True)
    subprocess.check_call(
        ["/usr/bin/systemctl", "restart", "systemd-resolved.service"]
    )
    sys.stdout.flush()
