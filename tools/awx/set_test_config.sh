#!/bin/bash

# set -euo pipefail

. ~/virtenv/py3/bin/activate

echo "Sending config from '/ansible-playbooks/tools/awx/test_config.json'"

tower-cli send /ansible-playbooks/tools/awx/test_config.json && echo "Done"

echo "Setting password for 'vagrant' user"
tower-cli credential modify --name=vagrant --inputs='{"username": "vagrant", "password": "vagrant"}'

template_id=$(tower-cli job_template get setup_linux_server -f id)

current_cred_id=$(tower-cli job_template get setup_linux_server -f json | jq -r ".summary_fields.credentials[].id")
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