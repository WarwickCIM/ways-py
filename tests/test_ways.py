"""Test module for backfillz."""

import pytest

from ways.ways import Ways


@pytest.fixture()
def compare_images(pytestconfig) -> bool:
    """Whether to compare generated images with stored expected images."""
    return pytestconfig.getoption("compare_images") == "True"


def test_WAYS(compare_images: bool) -> None:
    Ways()
    """WAYS object instantiates without error."""
