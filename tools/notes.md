* https://github.com/ansible/awx/issues/5228

`/tmp/awx-8.0.0/installer/roles/local_docker/tasks/main.yml`

```yaml
- name: Record Postgres version
  shell: cat "{{ postgres_data_dir }}/pgdata/PG_VERSION"
  changed_when: false
  register: old_pg_version
  when: pg_version_file.stat.exists

- name: Determine whether to upgrade postgres
  set_fact:
    upgrade_postgres: "{{ old_pg_version is defined and old_pg_version.stdout_lines[0] == '9.6' }}"



- name: Copy old pg_hba.conf
  copy:
    remote_src: yes
    src: "{{ postgres_data_dir + '/pgdata/pg_hba.conf' }}"
    dest: "{{ postgres_data_dir + '/10/data/' }}"
  when: upgrade_postgres | bool
```