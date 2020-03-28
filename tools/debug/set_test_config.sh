#!/bin/bash

. ~/virtenv/py3/bin/activate

set -euo pipefail

# tower-cli (https://github.com/ansible/tower-cli) is deprecated 
# New official tool AWX CLI (https://github.com/ansible/awx/tree/devel/awxkit/awxkit/cli/docs)
# doesn't look like a finished product as yet. For example, it is missing
# backup/restore functionality:
# https://github.com/ansible/awx/blob/devel/awxkit/awxkit/cli/docs/source/examples.rst#backuprestore
# So for now we stick with tower-cli

# First 'tower-cli send' call almost always behaves weirdly: it fails showing
# the message "Object is missing an asset type".
# Obviously, project.json does contain an asset type.
# Since the tool is deprecated, there is no much sense getting to the bottom of
# the issue - we just repeat the call several times until it succeeds.

echo "Sending project from '/opt/ansible-playbooks/tools/debug/awx_objects/project.json'"
for n in `seq 1 5`; do
  if (tower-cli send /opt/ansible-playbooks/tools/debug/awx_objects/project.json); then
    echo "Done"
    break
  fi
  sleep 5
  echo "Retrying"
done

echo "Sending credential from '/opt/ansible-playbooks/tools/debug/awx_objects/credential.json'"
tower-cli send /opt/ansible-playbooks/tools/debug/awx_objects/credential.json

echo "Setting password for 'vagrant' user"
tower-cli credential modify --name=vagrant --inputs='{"username": "vagrant", "password": "vagrant"}'

echo "Sending inventory from '/opt/ansible-playbooks/tools/debug/awx_objects/inventory.json'"
tower-cli send /opt/ansible-playbooks/tools/debug/awx_objects/inventory.json

echo "Sending job template from '/opt/ansible-playbooks/tools/debug/awx_objects/template.json'"
tower-cli send /opt/ansible-playbooks/tools/debug/awx_objects/template.json

echo "Setting credential for template 'check_if_reachable'"
template_id=$(tower-cli job_template get check_if_reachable -f id)

current_cred_id=$(tower-cli job_template get check_if_reachable -f json | jq -r ".summary_fields.credentials[].id")
if [ ! -z "${current_cred_id}" ]; then
  echo "Diassociating credential ${current_cred_id} from job template ${template_id}"
  curl --silent --user admin:password -H 'Content-Type: application/json' -X POST \
    -d "{\"disassociate\": true, \"id\": ${current_cred_id}}" \
    "http://localhost/api/v2/job_templates/${template_id}/credentials/"
fi

echo "Setting 'vagrant' as credential for job template ${template_id}"
cred_id=$(tower-cli credential get --name vagrant -f id)
curl --silent --user admin:password -H 'Content-Type: application/json' -X POST \
  -d "{\"id\": ${cred_id}}" \
  "http://localhost/api/v2/job_templates/${template_id}/credentials/"