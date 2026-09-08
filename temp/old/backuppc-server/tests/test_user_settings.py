import sys
import os
import pytest

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

@pytest.mark.usersettings
def test_server_user(host, pytestconfig):
    server_user_name = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_user_name",
        param_value=pytestconfig.getoption("user_name"),
        default_value="backuppc-server"
    )
    custom_data_dir_name = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_custom_data_dir",
        param_value=pytestconfig.getoption("custom_data_dir"),
        default_value=None
    )
    server_user = host.user(server_user_name)
    assert server_user.exists
    assert server_user.home == "/var/lib/backuppc"
    assert server_user.shell == "/bin/false"

    home_dir = host.file("/var/lib/backuppc")
    assert home_dir.exists

    if custom_data_dir_name:
        custom_data_dir = host.file(custom_data_dir_name)
        assert home_dir.exists
        assert home_dir.is_symlink
        assert home_dir.linked_to == custom_data_dir_name
        assert custom_data_dir.user == server_user_name
        assert custom_data_dir.group == server_user_name
        assert custom_data_dir.mode == 0o750
    else:
        assert home_dir.is_directory
        assert not home_dir.is_symlink
        assert home_dir.user == server_user_name
        assert home_dir.group == server_user_name
        assert home_dir.mode == 0o750
