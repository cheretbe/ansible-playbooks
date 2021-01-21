def pytest_addoption(parser):
    parser.addoption("--autoreboot", action="store_true", default=None)
    parser.addoption("--reboot-time", action="store", default=None)
