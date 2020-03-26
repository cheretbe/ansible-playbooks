ansible.config:
  file.managed:
    - source: salt://config/ansible.cfg
    - name: /home/vagrant/.ansible.cfg
    - template: jinja
    - user: vagrant
    - group: vagrant

ansible.local.inventory:
  file.managed:
    - source: salt://config/local_inventory.yml
    - name: /home/vagrant/local_inventory.yml
    - user: vagrant
    - group: vagrant

ansible.awx.inventory:
  file.managed:
    - source: salt://config/awx_inventory.tower.yml
    - name: /home/vagrant/awx_inventory.tower.yml

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

git.repo.symlink:
  file.symlink:
    - name: /home/vagrant/ansible-playbooks
    - target: /opt/ansible-playbooks