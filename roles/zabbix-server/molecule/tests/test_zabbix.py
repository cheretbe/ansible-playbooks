# pylint: disable=missing-module-docstring,missing-function-docstring
import os


def test_zabbix_running_and_enabled(host):
    zabbix_server_service = host.service("zabbix-server")
    assert zabbix_server_service.is_running
    assert zabbix_server_service.is_enabled


def test_apache_http_port_is_open(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_zabbix_server_version(host):
    # Temporarily use curl until HTTP module is implemented
    # https://github.com/philpep/testinfra/issues/407
    assert host.run_test(
        'curl -s http://localhost/zabbix/index.php -X POST '
        '-d "name=Admin&password=zabbix&enter=Sign+in" -c cookies.txt'
    ).rc == 0
    cmd = host.run(
        "curl -s http://localhost/zabbix/setup.php -b cookies.txt"
    )
    zabbix_ver_str = f"Zabbix {os.environ['EXPECTED_ZABBIX_VERSION']}"
    assert [s for s in cmd.stdout.split("\n") if zabbix_ver_str in s], \
        f"'{zabbix_ver_str}' string was not found in curl output"
