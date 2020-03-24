# ansible-playbooks

[Testlab readme](./tools/vagrant/testlab/README.md)

```shell
ansible-playbook -i localhost, --connection=local --become \
  /ansible-playbooks/run_role.yml --extra-vars "role_name=docker-ce"

/ansible-playbooks/tools/update_known_hosts.sh
```
`ansible_virtualization_role`, `ansible_virtualization_type`
 * https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/facts/virtual/linux.py
 
 ```yaml
- name: Gather package facts
  package_facts:
    manager: apt

- name: "Check if 'postfix' package is installed"
  set_fact:
    linux_mta_postfix_is_installed: "{{ ('postfix' in ansible_facts.packages)|bool }}"
```
 
Pywinrm

* https://docs.ansible.com/ansible-tower/latest/html/administration/kerberos_auth.html

```shell
ansible all -m "win_command" -a "cmd /c set" -i host.domain.tld, --extra-vars "ansible_user=user@DOMAIN.TLD ansible_connection=winrm ansible_port=5985 ansible_winrm_transport=kerberos"

ansible all -i 172.24.0.14, -m win_ping --extra-vars "ansible_user=vagrant ansible_connection=winrm ansible_port=5985 ansible_password=vagrant"

# Pre-requisites
# python-dev for Python 2
sudo apt install gcc python3-dev krb5-user libkrb5-dev
pip install kerberos requests_kerberos pywinrm
```
`/etc/krb5.conf`
```
[libdefaults]
    default_realm = DOMAIN.TLD

[realms]
    DOMAIN.TLD = {
      kdc = dc01.domain.tld
      admin_server = dc01.domain.tld
    }

[domain_realm]
.domain.tld = DOMAIN.TLD
```

```shell
# Execute BEFORE running Python script
# Enter domain name exactly like specified in /etc/krb5.conf (e.g. DOMAIN.TLD, not DOMAIN.tld)
kinit user@DOMAIN.TLD
klist
```

```python
import winrm

s = winrm.Session('host.domain.tld', auth=(None, None), transport='kerberos')
r = s.run_cmd('ipconfig', ['/all'])
print(r.std_out.decode("windows-1251"))
```

```shell
# Destroy all kerberos tickets
klist
kdestroy
```
```shell
ansible win_hosts -m "win_command" -a "cmd /c set"
ansible win_hosts -m raw -a "cmd /c set"
```
