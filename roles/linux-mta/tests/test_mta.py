def test_smtpd_is_active(host):
    assert host.socket("tcp://127.0.0.1:25").is_listening

# TODO: Add test to check local mail delivery
