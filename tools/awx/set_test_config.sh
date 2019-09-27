#!/bin/bash

# set -euo pipefail

. ~/virtenv/py3/bin/activate

echo "Sending config from '/ansible-playbooks/tools/awx/test_config.json'"

tower-cli send /ansible-playbooks/tools/awx/test_config.json && echo "Done"

echo "Setting password for 'vagrant' user"
tower-cli credential modify --name=vagrant --inputs='{"username": "vagrant", "password": "vagrant"}'