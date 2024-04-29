```shell
ansible win10 -m win_command -a "sc.exe config wuauserv start= demand"

# Default timeout is 600 (10 min)
ansible win10 -m win_reboot -a "reboot_timeout=1200"
```
