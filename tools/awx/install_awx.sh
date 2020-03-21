#!/bin/bash

set -euo pipefail

awx_version=${1-7.0.0}
echo "Installing AWX ${awx_version}"

ansible-playbook /ansible-playbooks/run_role.yml \
  --become \
  --extra-vars "role_name=ansible-awx-prerequisites ansible_awx_version=${awx_version}" \
  -i localhost, --connection=local

ansible-playbook "/tmp/awx-${awx_version}/installer/install.yml" \
  --become \
  -i "/tmp/awx-${awx_version}/installer/inventory" \
  -e @/opt/awx/install-options.yml