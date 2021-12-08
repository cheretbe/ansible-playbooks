### Notes

```yaml
# Mandatory parameters
purevpn_ovpn_client_server: "server"
purevpn_ovpn_client_user: "user"
purevpn_ovpn_client_password: "password"
# Optional parameters
purevpn_ovpn_client_protocol: "udp" # default is "tcp"
# purevpn_ovpn_client_operator_key
# purevpn_ovpn_client_keys_dir
```

### Debugging

```shell
resolvectl status
networkctl status --all

networkctl renew enp0s3

ln -sfn /run/systemd/resolve/resolv.conf /etc/resolv.conf

dev=ovpn-purevpn script_type=up \
  foreign_option_2="dhcp-option DNS 206.123.131.5" \
  foreign_option_1="dhcp-option DNS 206.123.131.3" \
  /host_home/projects/ansible-playbooks/purevpn-ovpn-client/files/update_resolve_conf.py
  
dev=ovpn-purevpn script_type=down \
  /host_home/projects/ansible-playbooks/purevpn-ovpn-client/files/update_resolve_conf.py
```