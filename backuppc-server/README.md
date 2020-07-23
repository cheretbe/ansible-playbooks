Testing
```shell
cd tools/vagrant/docker-tests/; vagrant up; finished
vagrant ssh -- 'cd /ansible-playbooks/backuppc-server; inv test'
```