#!/bin/bash

cat <<-EOF >/etc/apt/apt.conf.d/02proxy
  Acquire::http::proxy "http://${1}:3142";
  Acquire::ftp::proxy "${1}:3142";
EOF

cat <<-EOF >/etc/pip.conf
  [global]
  index-url = http://${1}:3141/root/pypi/+simple/
  trusted-host = ${1}
EOF

if [[ $(lsb_release -rs) == "20.04" ]]; then
  mkdir -p /etc/xdg/pip/
  ln -sf /etc/pip.conf /etc/xdg/pip/pip.conf
fi