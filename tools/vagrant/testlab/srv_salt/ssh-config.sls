{% if grains['os'] in ['CentOS', 'RedHat'] %}
  {% set ssh_service_name = 'sshd' %}
{% else %}
  {% set ssh_service_name = 'ssh' %}
{% endif %}

/etc/ssh/sshd_config:
  file.comment:
    - regex: ^PasswordAuthentication no

restart_ssh_on_config_change:
  service:
    - name: {{ ssh_service_name }}
    - running
    - enable: True
    - watch:
      - file: /etc/ssh/sshd_config
