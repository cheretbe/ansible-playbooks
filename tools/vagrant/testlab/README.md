`local-config.yml` example:
```yaml
---
use_awx: true
awx_version: 7.0.0
```

```shell
/ansible-playbooks/tools/awx/install_awx.sh && \
/ansible-playbooks/tools/awx/configure_tower_cli.sh && \
/ansible-playbooks/tools/awx/set_test_config.sh
```

* https://github.com/adamrushuk/ansible-azure/blob/master/vagrant/scripts/configure_ansible_awx.sh