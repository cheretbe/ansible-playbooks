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