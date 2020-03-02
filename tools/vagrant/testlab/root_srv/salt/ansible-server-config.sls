ansible.config:
  file.managed:
    - source: salt://config/ansible.cfg
    - name: /home/vagrant/.ansible.cfg

ansible.test.inventory:
  file.symlink:
    - name: /home/vagrant/test_inventory.yml
    - target: /vagrant/root_srv/salt/config/local_inventory.yml

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