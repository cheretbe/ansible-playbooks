import sys
import os
import pytest

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

def test_rsync_service(host, pytestconfig):
    if host.system_info.distribution == "ubuntu":
        rsync_service = host.service("rsync")
    elif host.system_info.distribution == "centos":
        rsync_service = host.service("rsyncd")
    else:
        raise Exception("Unsupported distribution: " + host.system_info.distribution)

    assert rsync_service.is_enabled
    assert rsync_service.is_running

    expected_rsync_address = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_client_rsync_address",
        param_value=pytestconfig.getoption("rsync_address"),
        default_value=""
    )

    if expected_rsync_address:
        assert host.socket(f"tcp://{expected_rsync_address}:873").is_listening
    else:
        assert host.socket("tcp://873").is_listening
