def test_no_custom_dir(host):
    assert host.file("/var/lib/backuppc").exists
    assert host.file("/var/lib/backuppc").is_directory
    assert not host.file("/var/lib/backuppc").is_symlink
    assert host.file("/var/lib/backuppc").user == "backuppc-server"
    assert host.file("/var/lib/backuppc").group == "backuppc-server"

def test_custom_dir(host):
    assert host.file("/var/lib/backuppc").exists
    assert host.file("/var/lib/backuppc").is_symlink
    assert host.file("/var/lib/backuppc").linked_to == "/custom/data/dir"
    assert host.file("/custom/data/dir").user == "backuppc-server"
    assert host.file("/custom/data/dir").group == "backuppc-server"
    assert host.file("/custom/data/dir").mode == 0o750
