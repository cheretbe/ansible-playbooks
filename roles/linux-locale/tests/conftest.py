def pytest_addoption(parser):
    parser.addoption("--default-lang", action="store", default=None)
    parser.addoption("--default-lc", action="store", default=None)
