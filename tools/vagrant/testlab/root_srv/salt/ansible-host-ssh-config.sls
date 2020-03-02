{% if grains['os'] in ['CentOS', 'RedHat'] %}
  {% set ssh_service_name = 'sshd' %}
{% else %}
  {% set ssh_service_name = 'ssh' %}
{% endif %}

/etc/ssh/sshd_config:
  file.comment:
    - regex: ^PasswordAuthentication no

restart.ssh.on.config.change:
  service:
    - name: {{ ssh_service_name }}
    - running
    - enable: True
    - watch:
      - file: /etc/ssh/sshd_config

vagrant.user.authorized_keys.entry:
  ssh_auth.present:
    - user: vagrant
    - source: salt://config/id_rsa.pub
    - config: '/home/vagrant/.ssh/authorized_keys'
