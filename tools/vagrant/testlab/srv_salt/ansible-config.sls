ansible_config_1:
  file.managed:
    - name: /etc/ansible/ansible.cfg
    - source: salt://config/ansible.cfg

ansible_config_2:
  file.managed:
    - name: /etc/ansible/hosts
    - source: salt://config/ansible_hosts