def pytest_addoption(parser):
    parser.addoption("--autoreboot", action="store_true", default=None)
    parser.addoption("--reboot-time", action="store", default=None)
    parser.addoption("--origins", action="append", default=None)
    parser.addoption("--additional-origins", action="append", default=None)
