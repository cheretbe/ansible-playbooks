def pytest_configure(config):
    # Register custom markers to avoid warnings
    config.addinivalue_line("markers", "usersettings")
    config.addinivalue_line("markers", "ver_backuppc_xs")
    config.addinivalue_line("markers", "ver_rsync_bpc")
    config.addinivalue_line("markers", "ver_backuppc")
    config.addinivalue_line("markers", "apache")

def pytest_addoption(parser):
    parser.addoption("--custom-data-dir", action="store", default=None)
    parser.addoption("--user-name", action="store", default=None)
    parser.addoption("--backuppc-version", action="store", default=None)
    parser.addoption("--backuppc-xs-version", action="store", default=None)
    parser.addoption("--rsync-bpc-version", action="store", default=None)
    parser.addoption("--apache-require", action="store", default=None)
