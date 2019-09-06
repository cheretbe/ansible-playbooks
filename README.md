# ansible-playbooks

* https://stackoverflow.com/questions/18195142/safely-limiting-ansible-playbooks-to-a-single-machine/18195217#18195217

```shell
# --check                 Dry run
# --limit ubuntu-xenial   Run only on selected hosts
# Run locally (note the trailing comma after 'localhost')
# -i localhost, --connection=local
ansible-playbook /ansible-roles/tools/run_role.yml --extra-vars "role_name=hello-world"

ansible localhost -m setup
```