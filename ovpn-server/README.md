### Notes

```yaml
# Mandatory parameters
ovpn_server_ca_cert:  /path/to/ca.crt
ovpn_server_cert:     /path/to/server.crt
ovpn_server_key:      /path/to/server.key
ovpn_server_dns_name: vpn.example.com

# Optional parameters
ovpn_server_port: "1194"
ovpn_server_protocol: udp
ovpn_server_dns_resolver: true
```

```shell
/etc/openvpn/server/client-config/make_client_config.sh client1 client1.crt client1.key
```
