base:
  '*':
  - etc_hosts

  'ansible':
    - linux-utils
    - ansible

  'ubuntu-bionic':
    - ssh-config

  'ubuntu-xenial':
    - ssh-config

  'centos-7':
    - ssh-config