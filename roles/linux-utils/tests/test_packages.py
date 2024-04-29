def test_packages_presence(host):
    package_names = [
        "mc", "htop", "net-tools", "ncdu", "wget", "git", "nano", "traceroute",
        "colordiff", "jq", "pv"
    ]

    if host.system_info.distribution == "ubuntu":
        package_names += ["dnsutils", "mtr-tiny"]
    elif host.system_info.distribution == "centos":
        package_names += ["bind-utils", "mtr"]
    else:
        raise Exception("Unsupported distribution: " + host.system_info.distribution)

    for package in package_names:
        assert host.package(package).is_installed
