host_ansible:
  host.present:
    - ip: 172.24.0.10
    - names:
      - ansible

host_ubuntu_bionic:
  host.present:
    - ip: 172.24.0.11
    - names:
      - ubuntu-bionic

host_ubuntu_xenial:
  host.present:
    - ip: 172.24.0.12
    - names:
      - ubuntu-xenial