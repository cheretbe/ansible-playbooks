```shell
# Get current versions
curl -s https://api.github.com/repos/backuppc/backuppc/releases/latest | jq -r ".tag_name"
curl -s https://api.github.com/repos/backuppc/backuppc-xs/releases/latest | jq -r ".tag_name"
curl -s https://api.github.com/repos/backuppc/rsync-bpc/releases/latest | jq -r ".tag_name"
```

```yaml
---
all:
  vars:
    ansible_user: vagrant
  hosts:
    ubuntu-focal:
      ansible_host: 172.24.0.11
    ubuntu-bionic:
      ansible_host: 172.24.0.12
backuppc:
  vars:
    # backuppc_server_version: "4.3.2"
    # backuppc_server_backuppc_xs_version: "0.59"
    # backuppc_server_rsync_bpc_version: "3.0.9.15"
    backuppc_server_data_dir: "/backuppc"
    backuppc_server_www_users:
      # vagrant/vagrant
      - 
        user_name: vagrant
        password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          39336565623162356332613063646162316638323165656363353032336338326634393531356566
          3036633335363130356131383035356230666662323038350a613566653863336336346261336232
          33303361356634313461316631323161363433653138386433366139353434386137653466383532
          6333643161303763630a656435326435663632623738376232306131633566346137356630653361
          3165
  hosts:
    ubuntu-focal:
    ubuntu-bionic:
```

Deployment test
```shell
read -s -p "Password: " AO_BACKUPPC_TEST_PASSWORD; echo ""; export AO_BACKUPPC_TEST_PASSWORD
AO_BACKUPPC_TEST_PASSWORD=vagrant /ansible-playbooks/tests/deployment/test_backuppc_server_deployment.py --www-user-name=vagrant
```

Testing
```shell
cd tools/vagrant/container-tests/; vagrant up; finished
vagrant ssh -- 'cd /ansible-playbooks/backuppc-server; inv test'; finished
```

Check if specific version upgrades to the latest version
```shell
# Check out version on an existing installation
grep "# Version" /usr/local/BackupPC/bin/BackupPC | cut -d"," -f1 | cut -d " " -f3
perl -e 'use lib "/usr/local/BackupPC/lib"; use BackupPC::XS; print $BackupPC::XS::VERSION . "\n"'
/usr/local/bin/rsync_bpc --version 2>&1 | head -n 1

# Install
ansible-playbook /ansible-playbooks/run_role.yml --extra-vars "role_name=backuppc-server" \
  --ask-vault-password \
  --extra-vars "backuppc_server_version=4.3.2 backuppc_server_backuppc_xs_version=0.59 \
  backuppc_server_rsync_bpc_version=3.0.9.15"
# Upgrade
ansible-playbook /ansible-playbooks/run_role.yml --extra-vars "role_name=backuppc-server" \
  --ask-vault-password

# Run upgrade test
cd /ansible-playbooks/backuppc-server
# Docker
inv upgrade --backuppc-from=4.3.2 --backuppc-xs-from=0.59 --rsync-bpc-from=3.0.9.15
```
