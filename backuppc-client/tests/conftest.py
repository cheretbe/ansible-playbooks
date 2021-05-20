def pytest_addoption(parser):
    parser.addoption("--user-name", action="store", default=None)
    parser.addoption("--ssh-public-key-file", action="store", default=None)
    parser.addoption("--use-test-sudo-entries", action="store_true", default=False)
