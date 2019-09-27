#!/bin/bash

if ! hash virtualenv 2>/dev/null; then
  sudo apt install -y virtualenv
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

echo "Waiting for AWX web interface to become available"
SECONDS=0
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:80)" -ne "200" ]]; do
    if [ $SECONDS -gt 300 ]; then
      >&2 echo "ERROR: Timeout waiting for AWX web interface (300s)"
      exit 1
    fi
    sleep 5
done
echo "Done"

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

echo "Waiting for data import to finish"
SECONDS=0
until tower-cli instance_group get tower >/dev/null 2>&1; do
    if [ $SECONDS -gt 300 ]; then
      >&2 echo "ERROR: Timeout waiting for data import to finish (300s)"
      exit 1
    fi
    sleep 5
done
echo "Done"