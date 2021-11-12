"""Test module for backfillz."""

import errno
import os
from typing import Any

from _pytest.config import Config
import altair as alt  # type: ignore
import geopandas as gpd  # type: ignore
import pandas as pd  # type: ignore
import pytest

from ways_py.ways import meta_hist


@pytest.fixture()
def headless(pytestconfig: Config) -> bool:
    """Whether tests are running in headless mode."""
    return str(pytestconfig.getoption("headless")) == "True"


# Plotly doesn't generate SVG deterministically; use PNG instead.
def expect_fig(fig: alt.Chart, filename: str, headless: bool) -> None:
    """Check for JSON-equivalence to stored image."""
    ext = 'json'
    have = fig.to_json()
    try:
        # Garbage collect any existing .new file
        new_filename: str = filename + '.new.' + ext
        if os.path.isfile(new_filename):
            os.remove(new_filename)

        file = open(filename + '.' + ext, 'r')
        expected = file.read()
        if expected != have:
            print(f"{filename}: differs from reference image.")
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), new_filename)
        print(f"{filename}: image identical.")
        if not headless:
            fig.show()
    except FileNotFoundError as e:
        file_new = open(e.filename, 'w')
        file_new.write(have)
        print(f"{filename}: creating new reference image.")
        alt.renderers.enable('mimetype')  # not sure what this is for
        if not headless:
            fig.show()
        assert False, f"{filename}: image changed."


@meta_hist
def example_choropleth(candidate_geo_states: pd.DataFrame, title: str, extent) -> alt.Chart:
    """Choropleth of the US states with the candidate vote percentage mapped to color."""
    scale = alt.Scale(type='band')
    color = alt.Color(shorthand='pct_estimate', bin=alt.Bin(maxbins=20), scale=scale)
    chart = alt.Chart(candidate_geo_states, title=title) \
        .mark_geoshape() \
        .encode(color, tooltip=['NAME', 'pct_estimate']) \
        .properties(width=500, height=300) \
        .project(type='albersUsa')

    if extent is not None:
        chart.encoding.color.bin.extent = extent

    return chart


def dataset() -> Any:
    """Dataset for choropleth example."""
    geo_states = gpd.read_file('notebooks/gz_2010_us_040_00_500k.json')
    df_polls = pd.read_csv('notebooks/presidential_poll_averages_2020.csv')
    trump_data = df_polls[df_polls.candidate_name == 'Donald Trump']
    trump_data.columns = [
        'cycle', 'NAME', 'modeldate', 'candidate_name', 'pct_estimate', 'pct_trend_adjusted'
    ]
    geo_states_trump = geo_states.merge(trump_data, on='NAME')
    return geo_states_trump[geo_states_trump.modeldate == '11/03/2020']


def test_altair_meta_hist(headless: bool) -> None:
    """Altair meta-histogram generates without error."""
    chart: alt.Chart = example_choropleth(dataset(), "Example choropleth", None)
    expect_fig(chart, "tests/expected_altair_meta_hist", headless)


def test_altair_meta_hist_extent(headless: bool) -> None:
    """Altair meta-histogram generates without error."""
    chart: alt.Chart = example_choropleth(dataset(), "Example choropleth", [0, 100])
    expect_fig(chart, "tests/expected_altair_meta_hist_extent", headless)
