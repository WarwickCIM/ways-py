def pytest_addoption(parser):  # type: ignore
    """Whether to compare generated images with stored expected images."""
    parser.addoption("--compare_images", action="store", default="True")
