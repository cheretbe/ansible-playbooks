:warning: Deprecated: use `docker-compose-projects` instead

Why this role is being used instead of [docker_compose](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_module.html) module?

As of 13.01.23 `docker_compose` module has a requirement: (docker-compose >= 1.7.0, < 2.0.0)[https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_module.html#ansible-collections-community-docker-docker-compose-module-requirements].
Therefore docker compose plugin v2.14.1, installed by 'docker-ce' role,
can't be used.

* https://github.com/ansible-collections/community.docker/issues/676#issuecomment-1656146970
* https://github.com/ansible-collections/community.docker/pull/586


```yaml
docker_compose_configs:
  seafile:
    env_variables:
      VAR1: 4.16.0
    local_settings:
     services:
       seafile:
         # 1Gb with no swap
         mem_limit: 1g
         memswap_limit: 1g
```
