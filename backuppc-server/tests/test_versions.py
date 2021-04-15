import sys
import os
import requests
import pytest

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

@pytest.mark.ver_backuppc_xs
def test_backuppc_xs_version(host, pytestconfig):
    expected_backuppc_xs_ver = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_backuppc_xs_version",
        param_value=pytestconfig.getoption("backuppc_xs_version"),
        default_value="latest"
    )
    if expected_backuppc_xs_ver == "latest":
        expected_backuppc_xs_ver = requests.get(
            "https://api.github.com/repos/backuppc/backuppc-xs/releases/latest"
        ).json()["tag_name"]
    backuppc_xs_ver = host.check_output(
        "perl -e '"
        "use lib \"/usr/local/BackupPC/lib\";"
        "use BackupPC::XS; print $BackupPC::XS::VERSION'"
    )
    assert expected_backuppc_xs_ver == backuppc_xs_ver
