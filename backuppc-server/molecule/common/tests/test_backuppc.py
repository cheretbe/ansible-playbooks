import os


def test_backuppc_running_and_enabled(host):
    backuppc_service = host.service("backuppc")
    assert backuppc_service.is_running
    assert backuppc_service.is_enabled


def test_apache_http_port_is_open(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_backuppc_status_page(host):
    # Temporarily use curl until HTTP module is implemented
    # https://github.com/philpep/testinfra/issues/407
    assert host.run_test(
            "curl -u backuppc:backuppc "
            "-s http://localhost/BackupPC_Admin | grep -q "
            "'BackupPC Server Status'"
        ).rc == 0

    if os.environ["EXPECTED_BACKUPPC_VERSION"] == "latest":
        cmd = host.run(
            "curl -s https://api.github.com/repos/backuppc/backuppc/"
            "releases/latest | jq -r '.tag_name'"
        )
        version_to_check = cmd.stdout.split("\n")[0]
    else:
        version_to_check = os.environ["EXPECTED_BACKUPPC_VERSION"]
    assert host.run_test(
            "curl -u backuppc:backuppc "
            "-s http://localhost/BackupPC_Admin | grep -q "
            "'%s'", version_to_check
        ).rc == 0, \
        f"Could not find version string '{version_to_check}'"
