#!/bin/bash

set -euo pipefail

ansible-playbook /ansible-playbooks/run_role.yml \
  --become \
  --extra-vars "role_name=ansible-awx-prerequisites ansible_awx_version=7.0.0" \
  -i localhost, --connection=local

ansible-playbook /tmp/awx-7.0.0/installer/install.yml \
  --become \
  -i /opt/awx/inventory