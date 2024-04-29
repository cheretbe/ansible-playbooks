#!/usr/bin/env python3

import sys
import os
import subprocess

sys.tracebacklimit = 0

print("Checking if a reboot of the system is necessary", flush=True)

if os.path.isfile("/bin/needs-restarting"):
    check_command = ["/bin/needs-restarting", "-r"]
elif os.path.isfile("/usr/bin/dnf"):
    check_command = ["/usr/bin/dnf", "needs-restarting", "-r"]
else:
    raise Exception(
        "ERROR: Neither '/bin/needs-restarting' nor '/usr/bin/dnf' couldn't be found"
    )

# proc = subprocess.run("exit 1", shell=True)
proc = subprocess.run(  # pylint: disable=subprocess-run-check
    check_command
)
if proc.returncode == 1:
    print("Rebooting the system", flush=True)
    subprocess.check_call(["/usr/sbin/reboot"], stdin=subprocess.DEVNULL)
