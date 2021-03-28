import pytest

def test_smartmontools_service(host):
    if host.ansible("setup")["ansible_facts"]["ansible_virtualization_role"] == "guest":
        pytest.skip()
    assert host.service("smartmontools").is_enabled
    assert host.service("smartmontools").is_running
