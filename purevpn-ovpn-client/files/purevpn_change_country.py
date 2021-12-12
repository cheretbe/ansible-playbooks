#!/usr/bin/env python3

import subprocess
import humanfriendly

current_server = None
with open("/etc/openvpn/client/purevpn.conf", "r", encoding="utf-8") as f:
    settings = f.read().splitlines()

for line in settings:
    setting = line.rstrip().split(" ", maxsplit=1)
    if setting[0] == "remote":
        current_server = setting[1]
        break

print("Select VPN server:")
new_server = humanfriendly.prompts.prompt_for_choice(
        [
            "cz2-auto-tcp.ptoserver.com 80",
            "nl2-auto-tcp.ptoserver.com 80",
            "ru2-auto-tcp.ptoserver.com 80",
            "de2-auto-tcp.ptoserver.com 80",
            "lt2-auto-tcp.ptoserver.com 80",
            "ro2-auto-tcp.ptoserver.com 80",
            "bg2-auto-tcp.ptoserver.com 80",
            "uk2-auto-tcp.ptoserver.com 80",
            "Exit"
        ],
        default=current_server
    )

if new_server != current_server:
    print(f"Changing server to '{new_server}'")

    for i, line in enumerate(settings):
        setting = line.rstrip().split(" ", maxsplit=1)
        if setting[0] == "remote":
            settings[i] = "remote " + new_server
            break

    with open("/etc/openvpn/client/purevpn.conf", "w", encoding="utf-8") as f:
        f.write("\n".join(settings))

    print("Restarting 'openvpn-client@purevpn' service")
    subprocess.check_call(["systemctl", "restart", "openvpn-client@purevpn"])
