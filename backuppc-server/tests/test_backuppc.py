import sys
import os
import requests

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

def test_backuppc_running_and_enabled(host):
    backuppc_service = host.service("backuppc")
    assert backuppc_service.is_running
    assert backuppc_service.is_enabled


def test_apache_http_port_is_open(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_backuppc_status_page(host, pytestconfig):
    # Temporarily use curl until HTTP module is implemented
    # https://github.com/philpep/testinfra/issues/407
    status_text = host.check_output(
        "curl -u backuppc:backuppc -s http://localhost/BackupPC_Admin"
    )

    assert "BackupPC Server Status" in status_text

    expected_backuppc_ver = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_version",
        param_value=pytestconfig.getoption("backuppc_version"),
        default_value="latest"
    )

    if expected_backuppc_ver == "latest":
        expected_backuppc_ver = requests.get(
            "https://api.github.com/repos/backuppc/backuppc/releases/latest"
        ).json()["tag_name"]

    backuppc_ver = "unknown"
    for line in status_text.splitlines():
        print("===>", line)
        if ", started at" in line:
            backuppc_ver = line.split(", started at")[0]
            backuppc_ver = backuppc_ver.split("version ")[1]

    assert expected_backuppc_ver == backuppc_ver
