#!/usr/bin/env python3

import sys
import os
import types
import subprocess
import json
import yaml
import shutil

def run_dialog(parameters):
    dialog_cmd = ["dialog"] + parameters
    dialog_env = os.environ.copy()
    # By default dialog returns 255 on ESC. It gets mixed up with error code -1
    # converted to unsigned 8-bit. We set DIALOG_ESC variable to use the same
    # code as Cancel since we don't need to distinguish ESC and Cancel.
    dialog_env["DIALOG_ESC"] = "1"
    proc = subprocess.Popen(dialog_cmd, stderr = subprocess.PIPE, env=dialog_env)
    stderr = proc.communicate()[1]
    if proc.returncode == 1:
        sys.exit("Cancelled by user")
    elif proc.returncode != 0:
        print(stderr.decode("utf-8"))
        raise subprocess.CalledProcessError(proc.returncode, dialog_cmd, output=stderr)
    else:
        return stderr.decode("utf-8")

def load_roles():
    roles = []
    for dir_entry in os.listdir("/ansible-playbooks"):
        full_path = os.path.join("/ansible-playbooks", dir_entry)
        if os.path.isdir(full_path):
            role_info = read_role_info(dir_entry, full_path)
            if not role_info is None:
                roles.append(role_info)
    return roles

def read_role_info(role_name, role_path):
    role_info = None
    if os.path.isfile(os.path.join(role_path, "tasks", "main.yml")):
        role_info = types.SimpleNamespace()
        role_info.name = role_name
        vars_file = os.path.join(role_path, "defaults", "main.yml")
        if os.path.isfile(vars_file):
            with open(vars_file, "r") as f:
                role_info.default_vars = yaml.safe_load(f)
        else:
            role_info.default_vars = None
    return role_info

if shutil.which("dialog") is None:
    sys.exit("ERROR: Command 'dialog' is not found. Please install corresponding package")

config_file_name = os.path.expanduser("~/.cache/cheretbe/ansible-playbooks/run_role_cfg.json")
if os.path.isfile(config_file_name):
    with open(config_file_name) as f:
        config = json.load(f)
else:
    config = {}

roles = load_roles()
roles.sort(key=lambda x: x.name)

last_used_role = config.get("last_used_role", None)
last_used_role_idx = None
dialog_list = []
for idx, i in enumerate(roles):
    dialog_list += [str(idx), i.name]
    if last_used_role and (i.name == last_used_role):
        last_used_role_idx = idx
dialog_params = ["--keep-tite", "--no-tags", "--menu", "Select a role:",
    "0", "0", "0"] + dialog_list
if last_used_role_idx:
    dialog_params = ["--default-item", str(last_used_role_idx)] + dialog_params
selection = run_dialog(dialog_params)

current_role = roles[int(selection)].name
config["last_used_role"] = current_role
print(f"Using role '{current_role}'")

role_default_vars = roles[int(selection)].default_vars
last_used_custom_vars = None
if config.get("custom_vars", None):
    last_used_custom_vars = config["custom_vars"].get(current_role, None)
current_role_vars = {}
if not role_default_vars is None:
    caption_length = 0
    for var_name in role_default_vars:
        if len(var_name) > caption_length:
            caption_length = len(var_name)
    dialog_list = []
    for idx, key in enumerate(role_default_vars):
        var_value = ""
        if last_used_custom_vars:
            if key in last_used_custom_vars:
                var_value = last_used_custom_vars[key]
        dialog_list += [key + ":", str(idx + 1), "2", var_value, str(idx + 1),
            str(caption_length + 4), "100", "0"]
    selection = run_dialog(["--keep-tite", "--no-tags",
        "--form", f"Override variable values for role '{current_role}':", "0", "0", "0"] +
        dialog_list)
    dialog_vars = selection.split("\n")
    for idx, key in enumerate(role_default_vars):
        if dialog_vars[idx]:
            current_role_vars[key] = dialog_vars[idx]

if not config.get("custom_vars", None):
    config["custom_vars"] = {}
config["custom_vars"][current_role] = current_role_vars

inventory = json.loads(subprocess.check_output(["ansible-inventory",
    "--list", "--export"]))

inventory_groups = []
for group in inventory["all"]["children"]:
    if group in inventory:
        inventory_groups.append(group)

# inventory_groups += ["zzz"]
# inventory_groups = []

if len(inventory_groups) == 0:
    subprocess.run(["ansible-inventory", "--list"])
    sys.exit("ERROR: No groups were found in the inventory. Check inventory configuration")

if len(inventory_groups) == 1:
    print(f"'{inventory_groups[0]}' is the only group in the inventory. "
        "Auto-selecting it")
    current_group = inventory_groups[0]
else:
    dialog_list = []
    for idx, i in enumerate(inventory_groups):
        dialog_list += [str(idx), i]
    # --menu <text> <height> <width> <menu height> <tag1> <item1> ...
    selection = run_dialog(["--keep-tite", "--no-tags", "--menu", "Select a group:",
        "0", "0", "0"] + dialog_list)
    current_group = inventory_groups[int(selection)]

print(f"Using group '{current_group}'")

inventory_hosts = []
for host in inventory[current_group]["hosts"]:
    inventory_hosts.append(host)

dialog_list = []
for idx, i in enumerate(inventory_hosts):
    dialog_list += [str(idx), i, "on"]
selection = run_dialog(["--keep-tite", "--no-tags",
    "--checklist", f"Select hosts ({current_group}):", "0", "0", "0"] +
    dialog_list)
current_hosts = []
for host_idx in selection.split():
    current_hosts.append(inventory_hosts[int(host_idx)])

if len(current_hosts) == 0:
    sys.exit("No hosts were selected. Exiting")
print("Using hosts", current_hosts)

os.makedirs(os.path.dirname(config_file_name), exist_ok=True)
with open(config_file_name, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=4)
