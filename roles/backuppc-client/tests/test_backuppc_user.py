import sys
import os
import jinja2

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

def custom_lookup_func(param1, param2):
    if param1 == "file":
        with open(param2, "r") as fh:
            return fh.read().strip()
    return ""

def test_user_settings(host, pytestconfig):
    expected_user_name = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_client_user_name",
        param_value=pytestconfig.getoption("user_name"),
        default_value="backuppc"
    )
    user_info = host.user(expected_user_name)
    assert user_info.exists

    expected_ssh_pub_key = pytestconfig.getoption("ssh_public_key_file")
    if expected_ssh_pub_key is None:
        expected_ssh_pub_key = test_utils.get_parameter_value(
            host=host,
            ansible_var_name="backuppc_client_ssh_auth_key",
            param_value=None,
            default_value=None
        )
        if "{{" in expected_ssh_pub_key:
            env = jinja2.Environment(undefined=jinja2.StrictUndefined)
            env.globals["lookup"] = custom_lookup_func
            expected_ssh_pub_key = env.from_string(expected_ssh_pub_key).render()
    else:
        with open(expected_ssh_pub_key, "r") as fh:
            expected_ssh_pub_key = fh.read().strip()
    keys = host.file(user_info.home + "/.ssh/authorized_keys").content_string.split("\n")
    assert expected_ssh_pub_key in keys

    expected_sudoers_entries = [
        {
            "command": "/usr/bin/rsync",
            "comment": f"Allow {expected_user_name} to read files with rsync over SSH"
        }
    ]
    # Most likely it's possible to pass an array of dictionaries from Molecule's
    # YAML to Testinfra as a parameter. But definitely it's not going to be easy :)
    # So instead of wrestling with ugly escaping we just use hard-coded value
    # for tests.
    if pytestconfig.getoption("use_test_sudo_entries"):
        expected_sudoers_entries += [
            {"command": "/etc/custom/command_1", "comment": "Test command 1"},
            {"command": "/etc/custom/command_2", "comment": "Test command 2"}
        ]
    else:
        expected_sudoers_entries += test_utils.get_parameter_value(
            host=host,
            ansible_var_name="backuppc_client_custom_sudo_commands",
            param_value=None,
            default_value=[]
        )
    sudoers_entries = host.file("/etc/sudoers.d/backuppc").content_string.split("\n")
    for entry in expected_sudoers_entries:
        print(entry)
        assert f"# {entry['comment']}" in sudoers_entries
        assert f"{expected_user_name} ALL=NOPASSWD: {entry['command']}" in sudoers_entries
