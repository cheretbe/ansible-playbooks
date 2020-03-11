#!/usr/bin/env python

import subprocess

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

cmd = ["dialog", "--title", "Enter the correct path:",
    "--form", "", "0", "0", "0",
    "PATH_FOR_FILE_ARCHIVING: ", "1", "1", "default1", "1", "25", "100", "0",
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