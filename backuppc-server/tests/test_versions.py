import sys
import os
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
        expected_backuppc_xs_ver = test_utils.get_github_release_info(
            "backuppc/backuppc-xs/releases/latest"
        )["tag_name"]
    backuppc_xs_ver = host.check_output(
        "perl -e '"
        "use lib \"/usr/local/BackupPC/lib\";"
        "use BackupPC::XS; print $BackupPC::XS::VERSION'"
    )
    assert expected_backuppc_xs_ver == backuppc_xs_ver

@pytest.mark.ver_rsync_bpc
def test_rsync_bpc_version(host, pytestconfig):
    expected_rsync_bpc_ver = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_rsync_bpc_version",
        param_value=pytestconfig.getoption("rsync_bpc_version"),
        default_value="latest"
    )
    if expected_rsync_bpc_ver == "latest":
        expected_rsync_bpc_ver = test_utils.get_github_release_info(
            "backuppc/rsync-bpc/releases/latest"
        )["tag_name"]
    rsync_bpc_ver = host.run_test(
        "/usr/local/bin/rsync_bpc --version"
    ).stderr.splitlines()[0].split()[2]
    assert expected_rsync_bpc_ver == rsync_bpc_ver

@pytest.mark.ver_backuppc
def test_backuppc_version(host, pytestconfig):
    expected_backuppc_ver = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_version",
        param_value=pytestconfig.getoption("backuppc_version"),
        default_value="latest"
    )
    if expected_backuppc_ver == "latest":
        expected_backuppc_ver = test_utils.get_github_release_info(
            "backuppc/backuppc/releases/latest"
        )["tag_name"]
    backuppc_ver = "unknown"
    for line in host.file("/usr/local/BackupPC/bin/BackupPC").content_string.splitlines():
        if "# Version" in line:
            backuppc_ver = line.split(",")[0].replace("# Version ", "")
    assert expected_backuppc_ver == backuppc_ver
