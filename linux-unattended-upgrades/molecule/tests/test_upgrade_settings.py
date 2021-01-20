import pytest

def file_contains_line(host, file_name, line):
    file_lines = host.file(file_name).content_string.split("\n")
    return line in file_lines

@pytest.fixture()
def autoreboot(pytestconfig):
    return pytestconfig.getoption("autoreboot")

@pytest.fixture()
def reboot_time(pytestconfig):
    return pytestconfig.getoption("reboot_time")

def test_settings(host):
    reboot_script = host.file(
        "/opt/ansible-scripts/unattended_upgrades/check_if_reboot_is_needed.py"
    )

    if host.system_info.distribution == "ubuntu":
        assert host.package("unattended-upgrades").is_installed
        assert host.file("/etc/apt/apt.conf.d/90-ansible-unattended-upgrades").exists
        assert not reboot_script.exists
    elif host.system_info.distribution == "centos":
        if host.system_info.release == '7':
            assert host.package("yum-cron").is_installed
            assert file_contains_line(host, "/etc/yum/yum-cron.conf", "apply_updates = yes")
        elif host.system_info.release == '8':
            assert host.package("dnf-automatic").is_installed
            assert file_contains_line(host, "/etc/dnf/automatic.conf", "apply_updates = yes")
        assert reboot_script.mode == 0o755

def test_reboot_settings(host, autoreboot, reboot_time): # pylint: disable=redefined-outer-name
    cron_file = host.file("/etc/cron.d/ansible_unattended_upgrade_reboot")

    if host.system_info.distribution == "ubuntu":
        assert not cron_file.exists
        apt_conf_file = host.file("/etc/apt/apt.conf.d/90-ansible-unattended-upgrades")
        assert apt_conf_file.exists
        if autoreboot:
            assert apt_conf_file.contains('Unattended-Upgrade::Automatic-Reboot "true";')
            assert apt_conf_file.contains(
                f'Unattended-Upgrade::Automatic-Reboot-Time "{reboot_time}";'
            )
        else:
            assert not apt_conf_file.contains('Unattended-Upgrade::Automatic-Reboot "true";')
            assert not apt_conf_file.contains(
                f'Unattended-Upgrade::Automatic-Reboot-Time "{reboot_time}";'
            )
    else:
        if autoreboot:
            assert cron_file.exists
            cron_time = reboot_time.split(":")
            cron_line = (
                # file.contains calls grep under the hood therefore we need to
                # escape star symbols
                f"{cron_time[1]} {cron_time[0]} \\* \\* \\* root "
                "systemd-cat -t ansible-unattended-upgrades "
                "/opt/ansible-scripts/unattended_upgrades/check_if_reboot_is_needed.py"
            )
            assert cron_file.contains(cron_line)
        else:
            assert not cron_file.exists
