#!/bin/bash

# set -euo pipefail

. ~/virtenv/py3/bin/activate

echo "Saving current config to '/ansible-playbooks/tools/awx/test_config.json'"

tower-cli receive --all > /ansible-playbooks/tools/awx/test_config.json && echo "Done"