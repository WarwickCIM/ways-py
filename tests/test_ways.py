"""Test module for backfillz."""

import errno
import os

from _pytest.config import Config
import altair as alt  # type: ignore
import geopandas as gpd  # type: ignore
import pandas as pd  # type: ignore
import pytest

from ways_py.ways import Ways


@pytest.fixture()
def compare_images(pytestconfig: Config) -> bool:
    """Whether to compare generated images with stored expected images."""
    return str(pytestconfig.getoption("compare_images")) == "True"


# Plotly doesn't generate SVG deterministically; use PNG instead.
def expect_fig(fig: alt.Chart, filename: str, check: bool) -> None:
    """Check for JSON-equivalence to stored image."""
    ext = 'json'
    if check:
        found = fig.to_json()
        try:
            file = open(filename + '.' + ext, 'r')
            expected = file.read()
            if expected != found:
                print(f"{filename}: differs from reference image.")
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename + '.new.' + ext)
            print(f"{filename}: image identical.")
#           fig.show()
        except FileNotFoundError as e:
            file_new = open(e.filename, 'w')
            file_new.write(found)
            print(f"{filename}: creating new reference image.")
            alt.renderers.enable('mimetype')
            fig.show()
            assert False
    else:
        print(f"{filename}: image not compared.")


def test_dummy_chart(compare_images: bool) -> None:
    """WAYS object instantiates without error."""
    fig: alt.Chart = Ways().dummy_chart()
    expect_fig(fig, "tests/expected_dummy_chart", compare_images)


def test_altair_meta_hist(compare_images: bool) -> None:
    """Altair meta-histogram generates without error."""
    geo_states = gpd.read_file('notebooks/choropleth_teaching/gz_2010_us_040_00_500k.json')
    df_polls = pd.read_csv('notebooks/choropleth_teaching/presidential_poll_averages_2020.csv')
    trump_data = df_polls[
        df_polls.candidate_name == 'Donald Trump'
    ]

    trump_data.columns = [
        'cycle', 'NAME', 'modeldate', 'candidate_name', 'pct_estimate', 'pct_trend_adjusted'
    ]
    geo_states_trump = geo_states.merge(trump_data, on='NAME')
    candidate_geo_states = geo_states_trump[
        (geo_states_trump.modeldate == '11/03/2020')
    ]
    scale = alt.Scale(type='band')
    column = 'pct_estimate'
    color = alt.Color(column, bin=True, scale=scale)
    bin = alt.Bin(maxbins=100, extent=[0, 100])
    fig: alt.Chart = Ways.altair_meta_hist(candidate_geo_states, column, bin, color)
    expect_fig(fig, "tests/expected_altair_meta_hist", compare_images)
