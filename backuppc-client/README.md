
```yml
---
# Default is 'backuppc'
backuppc_client_user_name: "user_name"

# [!] Has to be defined, default is empty. Single line, no breaks
backuppc_client_ssh_auth_key: "ssh-rsa AAAA...== BackuppPC"
# or use external file
backuppc_client_ssh_auth_key: "{{ lookup('file', '/home/user/.ssh/id_rsa.pub') }}"

# Default is empty
backuppc_client_custom_sudo_commands:
  - { comment: "Allow backuppc to create GitLab server backups", command: "/backup/scripts/backup_gitlab.sh" }
```