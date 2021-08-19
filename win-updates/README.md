```shell
ansible win10 -m win_command -a "sc.exe config wuauserv start= demand"
```
