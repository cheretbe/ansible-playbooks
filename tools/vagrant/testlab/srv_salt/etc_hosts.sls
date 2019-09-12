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

host_centos_7:
  host.present:
    - ip: 172.24.0.13
    - names:
      - centos-7

# Disable cloud-init to prevent unwanted /etc/hosts updates
/etc/cloud/cloud-init.disabled:
  file.managed:
    - create: true