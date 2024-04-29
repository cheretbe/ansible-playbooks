def pytest_addoption(parser):
    parser.addoption("--rsync-address", action="store", default=None)
