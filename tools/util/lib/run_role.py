# No shebang as this script is intended to be run via bash wrapper

import os
import sys
import pathlib
import subprocess
import argparse
import tempfile
import PyInquirer
import ansible.cli.inventory
import ansible.constants
import ansible.inventory.manager
import ansible.parsing.dataloader
import ansible.parsing.vault
# https://github.com/ansible/ansible/blob/stable-2.10/lib/ansible/vars/manager.py
import ansible.vars.manager
import common

def iterate_variables(var_list):
    local_copy = var_list.copy()
    for internal in ansible.cli.inventory.INTERNAL_VARS:
        if internal in local_copy:
            del local_copy[internal]
    # Vault strings use lazy evaluation. To trigger an exception we need to
    # actualy use varaible values
    for var_name in local_copy:
        str(local_copy[var_name])


def get_variables(inv_object, var_manager):
    if isinstance(inv_object, ansible.inventory.group.Group):
        for child_group in inv_object.child_groups:
            get_variables(child_group, var_manager)
        for host in inv_object.hosts:
            get_variables(host, var_manager)
        iterate_variables(inv_object.get_vars())
    else:
        iterate_variables(
            var_manager.get_vars(host=inv_object, include_hostvars=False)
        )


def get_target_needs_vault_password(target, var_manager):
    # Here we check if selected group or host contains (directly of indirectly)
    # variable(s) containing vault-encrypted strings. For this we iterate all
    # variable values without providing vault password and wait for AnsibleVaultError
    # exception. If no exception pops up, we assume that target doesn't need
    # vault password for role execution
    try:
        get_variables(target, var_manager)
    except ansible.parsing.vault.AnsibleVaultError:
        return True
    return False


def get_target(inventory):
    inv_groups = sorted(inventory.groups.values(), key=lambda x: x.name)
    inv_hosts = sorted(inventory.hosts.values(), key=lambda x: x.name)
    if len(inv_hosts) == 0:
        sys.exit("ERROR: Host list is empty")

    choices = [PyInquirer.Separator("==== Groups ====")]
    choices.extend([{"name": f"  [{group.name}]", "value": group} for group in inv_groups])

    choices.append(PyInquirer.Separator("==== Hosts ===="))
    choices.extend([{"name": f"  {host.name}", "value": host} for host in inv_hosts])

    return common.select_from_list(
        "Select a group or a host (Ctrl+C to cancel)",
        choices
    )


def get_role(roles_dir):
    roles = []
    for child_obj in roles_dir.iterdir():
        if child_obj.is_dir():
            if (child_obj / "tasks" / "main.yml").exists():
                roles.append(child_obj.name)
    roles.sort()

    return str(roles_dir / common.select_from_list(
        "Select a role to run (Ctrl+C to cancel)",
        roles
    ))


def check_vault_env_variable():
    if os.environ.get("ANSIBLE_VAULT_PASSWORD") is None:
        pwd = common.read_input("Enter vault password", "", is_password=True)
        os.environ["ANSIBLE_VAULT_PASSWORD"] = pwd
        return pwd

    return ""


def main():

    parser = argparse.ArgumentParser(description="Runs a single role")
    parser.add_argument(
        "-p", "--env-var-pipe-handle", type=int, default=-1,
        help="File handle for a named pipe to return ANSIBLE_VAULT_PASSWORD env variable"
    )
    options = parser.parse_args()

    vault_pwd_to_return = ""

    try:
        loader = ansible.parsing.dataloader.DataLoader()
        inventory = ansible.inventory.manager.InventoryManager(
            loader=loader,
            # Somehow DEFAULT_HOST_LIST is there ¯\_( ツ )_/¯
            sources=ansible.constants.DEFAULT_HOST_LIST # pylint: disable=no-member
        )
        var_manager = ansible.vars.manager.VariableManager(
            loader=loader, inventory=inventory
        )

        target = get_target(inventory)

        target_needs_vault_password = get_target_needs_vault_password(target, var_manager)
        temp_vault_pwd_file = None
        additional_params = []

        if target_needs_vault_password:
            vault_pwd_to_return = check_vault_env_variable()

        # ../../..
        roles_dir = pathlib.Path(__file__).resolve().parents[3]
        role = get_role(roles_dir)

        if target_needs_vault_password:
            temp_vault_pwd_file = tempfile.NamedTemporaryFile(delete=False, mode="w+t")

        try:
            if not temp_vault_pwd_file is None:
                print("Using ANSIBLE_VAULT_PASSWORD environment variable as a vault password")
                # Ansible doesn't have an option to pass vault password as an
                # environment variable. This feature was suggested, but will
                # not be implemented:
                # https://github.com/ansible/ansible/issues/45214
                # We use a temporary proxy script as a workaround
                additional_params = ["--vault-password-file", temp_vault_pwd_file.name]
                temp_vault_pwd_file.writelines([
                    "#!/bin/bash\n",
                    "echo ${ANSIBLE_VAULT_PASSWORD}\n"
                ])
                temp_vault_pwd_file.close()
                os.chmod(temp_vault_pwd_file.name, 0x744)

            subprocess.check_call(
                [
                    "ansible-playbook",
                    roles_dir / "run_role.yml",
                    "--limit", target.name,
                    "--extra-vars", f'role_name={role}'
                ] + additional_params
            )
        finally:
            if not temp_vault_pwd_file is None:
                os.unlink(temp_vault_pwd_file.name)
    finally:
        if options.env_var_pipe_handle != -1:
            with os.fdopen(options.env_var_pipe_handle, "w") as env_var_pipe_fd:
                env_var_pipe_fd.write(f"{vault_pwd_to_return}\n")

if __name__ == "__main__":
    main()
