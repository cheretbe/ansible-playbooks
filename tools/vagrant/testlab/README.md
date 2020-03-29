`local-config.yml` example:
```yaml
---
use_awx: true
awx_version: 7.0.0
docker_mirror: "http://localhost:5000"
ansible_vm_memory: "6144"
ansible_vm_cpus: "2"
```

```shell
~/ansible-playbooks/tools/awx/install_awx.sh && \
~/ansible-playbooks/tools/awx/configure_tower_cli.sh && \
~/ansible-playbooks/tools/awx/set_test_config.sh
```

```shell
. virtenv/py3/bin/activate

tower-cli receive --project ansible-playbooks > \
  /opt/ansible-playbooks/tools/debug/awx_objects/project.json
tower-cli receive --credential vagrant > \
  /opt/ansible-playbooks/tools/debug/awx_objects/credential.json
tower-cli receive --job_template check_if_reachable > \
  /opt/ansible-playbooks/tools/debug/awx_objects/template.json
tower-cli receive --inventory test_inventory > \
  /opt/ansible-playbooks/tools/debug/awx_objects/inventory.json
```

* https://github.com/adamrushuk/ansible-azure/blob/master/vagrant/scripts/configure_ansible_awx.sh