### Notes

```yaml
# Mandatory parameters
win_vpn_client_user_name: "user" # Windows user name to configure
win_vpn_client_ssh_key: "/path/to/a/key/on/ansible/host"
win_vpn_client_router: "192.168.0.1"
win_vpn_client_router_user: "user"
```

### Debugging

```shell
# Note single quotes for win_vpn_client__keys_dir parameter
ansible-playbook -l win10 /ansible-playbooks/run_role.yml \
  --extra-vars "role_name=win-vpn-client" \
  --extra-vars "win_vpn_client_user_name=vagrant" \
  --extra-vars 'win_vpn_client_ssh_key=/vagrant/temp/operator_key_openssh' \
  --extra-vars "win_vpn_client_router=172.24.0.11" \
  --extra-vars "win_vpn_client_router_user=vagrant"
```
