"""Test module for backfillz."""

import pytest


@pytest.fixture()
def compare_images(pytestconfig) -> bool:
    """Whether to compare generated images with stored expected images."""
    return pytestconfig.getoption("compare_images") == "True"
