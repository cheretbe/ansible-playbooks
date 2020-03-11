#!/usr/bin/env python3

import sys
import subprocess
import json

def run_dialog(parameters):
    dialog_cmd = ["dialog"] + parameters
    proc = subprocess.Popen(dialog_cmd, stderr = subprocess.PIPE)
    stderr = proc.communicate()[1]
    if proc.returncode in [1, 255]:
        sys.exit("Cancelled by user")
    elif proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, dialog_cmd, output=stderr)
    else:
        return stderr.decode("utf-8")


inventory = json.loads(subprocess.check_output(["ansible-inventory",
    "--list", "--export"]))

inventory_groups = []
for group in inventory["all"]["children"]:
    if group in inventory:
        inventory_groups.append(group)

# inventory_groups += ["zzz"]

if len(inventory_groups) == 1:
    print(f"'{inventory_groups[0]}' is the only group in the inventory. "
        "Auto-selecting it")
    current_group = inventory_groups[0]
else:
    dialog_list = []
    for idx, i in enumerate(inventory_groups):
        dialog_list += [str(idx), i]
    selection = run_dialog(["--keep-tite", "--no-tags", "--menu", "Select a group:",
        "0", "0", "0"] + dialog_list)
    current_group = inventory_groups[int(selection)]

    # run_dialog(["--keep-tite", "--title", "Enter the correct path:",
    # "--form", "", "0", "0", "0",
    # "PATH_FOR_FILE_ARCHIVING: ", "1", "1", "default1", "1", "27", "100", "0",
    # "PATH_FOR_PLACE_FOR_ARCHIVING: ", "2", "1", "default2", "2", "30", "100", "0"])


    #     group_hosts = inventory[group]["hosts"]
    # print(len(group_hosts))


# group_hosts = inventory.get("ungrouped"["hosts"]
# print(len(group_hosts))

print(current_group)
sys.exit(0)


# https://github.com/Risoko/Bash-Archiving-Script/blob/master/script_for_archiving.sh

# test = subprocess.check_output('dialog --title "Enter the correct path:" '
#     '--form ""     0 0 0 '
#     '"PATH_FOR_FILE_ARCHIVING: "         1 1 "default1"             1 25 100 0 '
#     '"PATH_FOR_PLACE_FOR_ARCHIVING: "    2 1  "default2"       2 30 100 0',
#     shell=True)
# test = subprocess.check_output("dialog --clear --stdout --title \"aaa\" --fselect bbb 10 50", shell=True)

cmd = ('dialog --title "Enter the correct path:" '
    '--form ""     0 0 0 '
    '"PATH_FOR_FILE_ARCHIVING: "         1 1 "default1"             1 25 100 0 '
    '"PATH_FOR_PLACE_FOR_ARCHIVING: "    2 1  "default2"       2 30 100 0')

# results = subprocess.run(cmd, stdout=subprocess.PIPE)
# test = results.stdout.rstrip().decode('utf-8')

# test = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
# test = subprocess.check_output(cmd, shell=True)

cmd = ["dialog", "--keep-tite", "--title", "Enter the correct path:",
    "--form", "", "0", "0", "0",
    "PATH_FOR_FILE_ARCHIVING: ", "1", "1", "default1", "1", "27", "100", "0",
    "PATH_FOR_PLACE_FOR_ARCHIVING: ", "2", "1", "default2", "2", "30", "100", "0"]

proc = subprocess.Popen(cmd,
    # stdout = subprocess.PIPE,
    stderr = subprocess.PIPE,
)
# stdout, stderr = proc.communicate()
stderr = proc.communicate()[1]
 
# print(proc.returncode, stdout, stderr)
print(proc.returncode, stderr)

# print("-----")
# print(test)