### Notes

```yaml
# Mandatory parameters
# ----------
# either (1)
router_lan_if_mac_addr: "08:00:27:e4:7e:86"
# or (2)
router_lan_if_name: "tun0"
# ----------

# ----------
# either (1)
router_wan_if_name: "ovpn-purevpn"
# or (2)
router_wan_if_mac_addr: "08:00:27:84:0f:13"
# or (3)
router_wan_if_ip_addr: "192.168.0.10"
# ----------

# Optional parameters
# Default is false
router_allow_wan_ssh: true
# Default is []
router_custom_ports:
  - {protocol: "tcp", port: 1194, comment: "Allow VPN"}
```

### Debugging

```shell
vboxmanage showvminfo --machinereadable $(cat .vagrant/machines/ubuntu-focal/virtualbox/id) | \
  grep macaddress2 | awk -F\" '{print tolower($2)}' | sed 's/\(..\)/\1:/g;s/:$//'

ansible-playbook -l ubuntu-focal /host_home/projects/ansible-playbooks/run_role.yml \
  --extra-vars "role_name=router" \
  --extra-vars "router_lan_mac_addr=08:00:27:e4:7e:86" \
  --extra-vars "router_wan_if_name=ovpn-purevpn"

ansible-playbook -l ubuntu-focal /host_home/projects/ansible-playbooks/run_role.yml \
  --extra-vars "role_name=router" \
  --extra-vars "router_lan_if_name=enp0s8" \
  --extra-vars "router_wan_if_ip_addr=10.0.2.15"
```
