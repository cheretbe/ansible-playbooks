#!/bin/bash

if ! hash virtualenv 2>/dev/null; then
  sudo apt install virtualenv
fi

if [ ! -f ~/virtenv/py3/bin/activate ]; then
  mkdir -p ~/virtenv
  virtualenv -p python3 ~/virtenv/py3
fi

. ~/virtenv/py3/bin/activate

if ! hash tower-cli 2>/dev/null; then
  pip install ansible-tower-cli
fi

tower-cli --version

if [[ $(tower-cli config username) == "username: " ]]; then
  echo "Setting username"
  tower-cli config username admin
fi
if [[ $(tower-cli config password) == "password: " ]]; then
  echo "Setting password"
  tower-cli config password password
fi
if [[ $(tower-cli config host) == "host: 127.0.0.1" ]]; then
  echo "Setting host to http://localhost:80"
  tower-cli config host http://localhost:80
fi
if [[ $(tower-cli config verify_ssl) == "verify_ssl: True" ]]; then
  echo "Turning of SSL verification"
  tower-cli config verify_ssl False
fi

tower-cli version