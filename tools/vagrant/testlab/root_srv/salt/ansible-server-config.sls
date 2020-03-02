#ansible_config_1:
#  file.managed:
#    - name: /etc/ansible/ansible.cfg
#    - source: salt://config/ansible.cfg

#ansible_config_2:
#  file.managed:
#    - name: /etc/ansible/hosts
#    - source: salt://config/ansible_hosts


vagrant.user.private.key:
  file.managed:
    - source: salt://config/id_rsa
    - name: /home/vagrant/.ssh/id_rsa
    - mode: 600
    - user: vagrant
    - group: vagrant

vagrant.user.public.key:
  file.managed:
    - source: salt://config/id_rsa.pub
    - name: /home/vagrant/.ssh/id_rsa.pub
    - mode: 644
    - user: vagrant
    - group: vagrant