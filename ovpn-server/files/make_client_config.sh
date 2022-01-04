#!/bin/bash

echo "Writing ${1}.ovpn"

cat /etc/openvpn/server/client-config/client_base.conf \
    <(echo -e '<ca>') \
    /etc/openvpn/server/ca.crt \
    <(echo -e '</ca>\n<cert>') \
    ${2} \
    <(echo -e '</cert>\n<key>') \
    ${3} \
    <(echo -e '</key>\n<tls-crypt>') \
    /etc/openvpn/server/ta.key \
    <(echo -e '</tls-crypt>') \
    > ${1}.ovpn
