### Notes

```yaml
# Mandatory parameters (ovpn_client_server_type == "purevpn")
ovpn_client_server: server
ovpn_client_purevpn_user: user
ovpn_client_purevpn_password: password

# Mandatory parameters (ovpn_client_server_type == "chere")
ovpn_client_server: server

# ----------
# either (1)
ovpn_client_chere_ta_key: "-----BEGIN OpenVPN Static key V1-----\
  00000000000000000000000000000000\
  00000000000000000000000000000000\
  -----END OpenVPN Static key V1-----"
# or (2)
ovpn_client_chere_ta_key_file: /path/to/ta.key
# ----------

# ----------
# either (1)
ovpn_client_chere_client_cert: "-----BEGIN CERTIFICATE-----\
  0000000000000000000000000000000000000000000000000000000000000000\
  000000000000000000000000000000000000000000000000000000==\
  -----END CERTIFICATE-----"
# or (2)
ovpn_client_chere_client_cert_file: /path/to/client1.crt
# ----------

# ----------
# either (1)
ovpn_client_chere_client_key: "-----BEGIN PRIVATE KEY-----\
  0000000000000000000000000000000000000000000000000000000000000000\
  0000000000000000000000000000000000000000000000000000000000000000\
  -----END PRIVATE KEY-----"
# or (2)
ovpn_client_chere_client_key_file: /path/to/client1.key
# ----------

# Optional parameters
ovpn_client_protocol: udp                  # default is "tcp"
ovpn_client_operator: username             # default is not defined
ovpn_client_operator_key: path/to/key/file # Required when ovpn_client_operator
                                           # parameter is defined
```

### Debugging

```shell
/host_home/projects/ansible-playbooks/tools/run_role.py \
  -l ubuntu-focal ovpn-client \
  --extra-vars "ovpn_client_server=cz2-auto-tcp.ptoserver.com" \
  --extra-vars "ovpn_client_server_type=purevpn" \
  --extra-vars "ovpn_client_purevpn_user=user" \
  --extra-vars "ovpn_client_purevpn_password=password"

/host_home/projects/ansible-playbooks/tools/run_role.py \
  -l ubuntu-focal ovpn-client \
  --extra-vars "ovpn_client_server=vpn.chere.one" \
  --extra-vars "ovpn_client_chere_ta_key_file=/host_home/temp/vpn/ta.key" \
  --extra-vars "ovpn_client_chere_client_cert_file=/host_home/temp/vpn/client1.crt" \
  --extra-vars "ovpn_client_chere_client_key_file=/host_home/temp/vpn/client1.key"
```

```shell
ansible-playbook -l ubuntu-focal /ansible-playbooks/run_role.yml \
  --extra-vars "role_name=purevpn-ovpn-client" \
  --extra-vars "purevpn_ovpn_client_server=cz2-auto-udp.ptoserver.com" \
  --extra-vars "purevpn_ovpn_client_user=user" \
  --extra-vars "purevpn_ovpn_client_password=password" \
  --extra-vars "ovpn_client_operator_key=/vagrant/.vagrant/machines/ubuntu-focal/virtualbox/private_key" \
  --extra-vars "ovpn_client_keys_dir=/vagrant/temp" \
  --extra-vars "ovpn_client_operator=vagrant"

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