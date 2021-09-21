"""Test module for backfillz."""

import errno
import os

import altair as alt
import pytest

from ways_py.ways import Ways


@pytest.fixture()
def compare_images(pytestconfig) -> bool:
    """Whether to compare generated images with stored expected images."""
    return pytestconfig.getoption("compare_images") == "True"


# Plotly doesn't generate SVG deterministically; use PNG instead.
def expect_fig(fig: alt.Chart, filename: str, check: bool) -> None:
    """Check for pixel-for-pixel equivalence to stored image."""
    ext = "png"
    if check:
        found = fig.to_image(format=ext)
        try:
            file = open(filename + "." + ext, "rb")
            expected = file.read()
            if expected != found:
                print(f"{filename}: differs from reference image.")
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename + ".new." + ext)
            print(f"{filename}: image identical.")
#            fig.show(config=default_config())
        except FileNotFoundError as e:
            file_new = open(e.filename, "wb")
            file_new.write(found)
            print(f"{filename}: creating new reference image.")
            fig.show(config=default_config())
            assert False
    else:
        print(f"{filename}: image not compared.")


def test_dummy_chart(compare_images: bool) -> None:
    fig: alt.Chart = Ways().dummy_chart()
    expect_fig(fig, "tests/expected_dummy_chart", compare_images)

    """WAYS object instantiates without error."""
