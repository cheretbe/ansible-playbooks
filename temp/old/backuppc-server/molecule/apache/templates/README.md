This is a workaround for converge playbook not finding templates directory.
We include tasks from config_apache.yml, not the role itself, therefore
'search magic' is not applied to the role directory (https://docs.ansible.com/ansible/latest/user_guide/playbook_pathing.html#the-magic-of-local-paths
).

Prepare playbook copies needed template files here.