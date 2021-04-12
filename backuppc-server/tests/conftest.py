def pytest_configure(config):
    # Register custom markers to avoid warnings
    config.addinivalue_line("markers", "usersettings")

def pytest_addoption(parser):
    parser.addoption("--custom-data-dir", action="store", default=None)
    parser.addoption("--user-name", action="store", default=None)