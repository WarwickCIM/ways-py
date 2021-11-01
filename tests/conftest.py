def pytest_addoption(parser):  # type: ignore
    """Whether to compare generated images with stored expected images."""
    parser.addoption("--headless", action="store", default="False")
