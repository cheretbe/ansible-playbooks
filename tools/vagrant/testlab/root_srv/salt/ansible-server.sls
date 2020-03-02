ansible_repo:
  pkgrepo.managed:
    - ppa: ansible/ansible

ansible:
  pkg:
    - name: ansible
    - installed
    - require: [ansible_repo]