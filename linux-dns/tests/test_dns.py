def test_dns_stub_is_not_active(host):
    # A (bit ugly) workaround for this issue:
    # https://github.com/pytest-dev/pytest-testinfra/issues/355
    # On Ubuntu Bionic we temporarily remove /bin/ss to force testinfa
    # use netstat
    need_ss_workaround = (
        host.system_info.distribution == "ubuntu" and
        host.system_info.codename == "bionic" and
        host.file("/bin/ss").exists
    )
    if need_ss_workaround:
        host.run("sudo mv /bin/ss /bin/ss.bak")
    try:
        host_sockets = host.socket.get_listening_sockets()
    finally:
        if need_ss_workaround:
            host.run("sudo mv /bin/ss.bak /bin/ss")

    assert "tcp://127.0.0.53%lo:53" not in host_sockets
    assert "udp://127.0.0.53%lo:53" not in host_sockets
    assert not host.socket("tcp://127.0.0.53:53").is_listening
    assert not host.socket("udp://127.0.0.53:53").is_listening


def test_dns_resolving(host):
    assert host.addr("google.com").is_resolvable
