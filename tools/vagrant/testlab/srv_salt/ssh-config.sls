/etc/ssh/sshd_config:
  file.comment:
    - regex: ^PasswordAuthentication no

restart_ssh_on_config_change:
  service:
    - name: ssh
    - running
    - enable: True
    - watch:
      - file: /etc/ssh/sshd_config
