```shell
docker run -dti --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
  --publish=80:80 --name debug \
  geerlingguy/docker-ubuntu1804-ansible

# [!] Without this /usr/share/doc/zabbix-server-mysql/create.sql.gz
# file is not going to be created
docker exec debug rm /etc/dpkg/dpkg.cfg.d/excludes

ansible-playbook -i debug, --connection=docker \
  --extra-vars "zabbix_repo_version=4.4 ansible_python_interpreter=/usr/bin/python3" \
  /ansible-playbooks/zabbix_server_setup.yml

docker exec -ti debug /bin/bash

docker rm debug -f
```