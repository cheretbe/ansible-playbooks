import pytest

def get_parameter_value(host, ansible_var_name, param_value, default_value):
    if host.backend.HAS_RUN_ANSIBLE:
        ansible_var_value = host.ansible.get_variables().get(ansible_var_name, None)
    else:
        ansible_var_value = None
    return_value = ansible_var_value if param_value is None else param_value
    if return_value is None:
        return_value = default_value
    return return_value


def file_contains_line(host, file_name, line):
    file_lines = host.file(file_name).content_string.split("\n")
    return line in file_lines

def test_settings(host, pytestconfig):
    origins = get_parameter_value(
        host=host,
        ansible_var_name="unattended_allowed_origins",
        param_value=pytestconfig.getoption("origins"),
        default_value=[
            '"${distro_id}:${distro_codename}";',
            '"${distro_id}:${distro_codename}-security";',
            '"${distro_id}ESM:${distro_codename}";',
            '"${distro_id}:${distro_codename}-updates";'
        ]
    )

    origins += get_parameter_value(
        host=host,
        ansible_var_name="unattended_additional_allowed_origins",
        param_value=pytestconfig.getoption("additional_origins"),
        default_value=[]
    )

    reboot_script = host.file(
        "/opt/ansible-scripts/unattended_upgrades/check_if_reboot_is_needed.py"
    )

    if host.system_info.distribution == "ubuntu":
        apt_conf_file = host.file("/etc/apt/apt.conf.d/90-ansible-unattended-upgrades")
        assert host.package("unattended-upgrades").is_installed
        assert apt_conf_file.exists
        assert not reboot_script.exists
        for origin in origins:
            assert apt_conf_file.contains(origin)
    elif host.system_info.distribution == "centos":
        if host.system_info.release == '7':
            assert host.package("yum-cron").is_installed
            assert file_contains_line(host, "/etc/yum/yum-cron.conf", "apply_updates = yes")
        elif host.system_info.release == '8':
            assert host.package("dnf-automatic").is_installed
            assert file_contains_line(host, "/etc/dnf/automatic.conf", "apply_updates = yes")
        assert reboot_script.mode == 0o755

def test_reboot_settings(host, pytestconfig):
    autoreboot = get_parameter_value(
        host=host,
        ansible_var_name="unattended_automatic_reboot",
        param_value=pytestconfig.getoption("autoreboot"),
        default_value=False
    )
    reboot_time = get_parameter_value(
        host=host,
        ansible_var_name="unattended_automatic_reboot_time",
        param_value=pytestconfig.getoption("reboot_time"),
        default_value="02:00"
    )

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
