### Notes

```yaml
# Mandatory parameters
router_lan_mac_addr: "08:00:27:e4:7e:86"
router_wan_if_name: "ovpn-purevpn"
```

### Debugging

```shell
vboxmanage showvminfo --machinereadable $(cat .vagrant/machines/ubuntu-focal/virtualbox/id) | \
  grep macaddress2 | awk -F\" '{print tolower($2)}' | sed 's/\(..\)/\1:/g;s/:$//'

ansible-playbook -l ubuntu-focal /ansible-playbooks/run_role.yml \
  --extra-vars "role_name=router" \
  --extra-vars "router_lan_mac_addr=08:00:27:e4:7e:86" \
  --extra-vars "router_wan_if_name=ovpn-purevpn"
```
