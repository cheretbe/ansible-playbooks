base:
  '*':
#    - etc_hosts
    - linux-utils

  'ansible-vm':
    - ansible-server
    - ansible-server-config

  'ubuntu-focal':
    - ansible-host-ssh-config

  'ubuntu-bionic':
    - ansible-host-ssh-config

  'ubuntu-xenial':
    - ansible-host-ssh-config

  'centos-7':
    - ansible-host-ssh-config

  'centos-8':
    - ansible-host-ssh-config