#!/usr/bin/env python3

import time
import sys
import argparse
import subprocess
import packaging.version

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--batch-mode', action='store_true',
    default=False, help='Batch mode (upgrade AWX without confirmation)')
parser.add_argument("awx_version", nargs="?", default="7.0.0",
    help="AWX version to install (default: 7.0.0)")
parser.add_argument("-m", "--docker-mirror", dest="docker_mirror",
    help="Local Docker registry mirror (e.g. localhost:5000)")

options = parser.parse_args()

print(f"Installing AWX {options.awx_version}", flush=True)

proc = subprocess.Popen("sudo docker exec awx_task /usr/bin/awx-manage version",
    shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
version_str = proc.communicate()[0].decode("utf-8").split("\n")[0]
if proc.returncode == 0:
    if packaging.version.parse(version_str) >= packaging.version.parse(options.awx_version):
        print(f"AWX {version_str} does not need an upgrade to version {options.awx_version}")
        sys.exit(0)
    else:
        print(f"Upgrading AWX {version_str} to version {options.awx_version}", flush=True)

extra_vars = f'"role_name": "ansible-awx-prerequisites", "ansible_awx_version": "{options.awx_version}"'
if options.docker_mirror != "":
    extra_vars += f', "docker_ce_registry_mirrors": ["{options.docker_mirror}"]'
if options.batch_mode:
    extra_vars += ', "ansible_awx_force_upgrade": True'
subprocess.check_call(["ansible-playbook", "/ansible-playbooks/run_role.yml",
    "--become", "--extra-vars", "{" + extra_vars + "}", "-i", "localhost,",
    "--connection=local"])

subprocess.check_call(["ansible-playbook",
    f"/tmp/awx-{options.awx_version}/installer/install.yml",
    "--become",
    "-i", f"/tmp/awx-{options.awx_version}/installer/inventory",
    "-e", "@/opt/awx/install-options.yml"])

print("Waiting for data import to finish", flush=True)
start_time = time.time()
while True:
    awx_task_log = subprocess.check_output(
            ["sudo", "docker", "logs", "awx_task"],
            stderr=subprocess.STDOUT
        ).decode("utf-8").splitlines()
    if any("awx.main.tasks Cluster node heartbeat task" in s for s in awx_task_log):
        break
    if time.time() > (start_time + 600):
        sys.exit("ERROR: Timeout waiting for data import to finish (600s)")
    # print("debug: sleep 5s", flush=True)
    time.sleep(5)
print("Done", flush=True)