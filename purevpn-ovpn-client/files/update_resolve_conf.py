#!/usr/bin/python3

import sys
import os
import pathlib
import subprocess

# Why is this script needed:
# https://github.com/cheretbe/notes/blob/master/openvpn.md#dns
# We install own version of /etc/resolv.conf to make sure there is no DNS leakage

print(
    f"dev: {os.environ.get('dev', None)}, script_type: {os.environ.get('script_type', None)}",
    flush=True
)

if not os.environ.get("dev", None):
    sys.exit(0)
script_type = os.environ.get("script_type", None)
if not script_type:
    sys.exit(0)

if script_type == "up":
    vpn_dns_servers = []

    for env_var in os.environ:
        if env_var.startswith("foreign_option_"):
            print(env_var, os.environ[env_var])
            value_parts = os.environ[env_var].split(" ")
            if len(value_parts) == 3 and value_parts[0] == "dhcp-option" and value_parts[1] == "DNS":
                vpn_dns_servers += [value_parts[2]]
    if len(vpn_dns_servers) > 0:
        print(
            f"Updating /etc/resolv.conf to use the following DNS server(s): {vpn_dns_servers}",
            flush=True
        )
        os.unlink("/etc/resolv.conf")
        with open("/etc/resolv.conf", "w") as resolv_f:
            resolv_f.write("# Created by {}\n\n".format(pathlib.Path(__file__)))
            for dns_srv in vpn_dns_servers:
                resolv_f.write(f"nameserver {dns_srv}\n")
        # No need to restart dnsmasq service: it registers subscriber script
        # /etc/resolvconf/update.d/dnsmasq and updates nameservers when
        # /etc/resolv.conf is modified

elif script_type == "down":
    print("Restoring /etc/resolv.conf as a link to /run/systemd/resolve/resolv.conf", flush=True)
    os.unlink("/etc/resolv.conf")
    os.symlink("/run/systemd/resolve/resolv.conf", "/etc/resolv.conf")
    # When /etc/resolv.conf is not symlinked to /run/systemd/resolve/resolv.conf,
    # systemd-resolved parses /etc/resolv.conf contents and uses nameserver entries.
    # We restart it to make sure it doesn't pick up our nameservers, that are
    # going to become unreachable
    print("Restarting systemd-resolved service", flush=True)
    subprocess.check_call(
        ["/usr/bin/systemctl", "restart", "systemd-resolved.service"]
    )
    sys.stdout.flush()
