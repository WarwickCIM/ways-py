"""Test module for backfillz."""

import inspect
import math
import os
from typing import Any, List, Optional

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


def expect_fig(fig: alt.Chart, filename: str, headless: bool) -> None:
    """Check for equivalence to stored output baselines.

    The tests rely on altair_saver (https://pypi.org/project/altair-saver/), which in turn needs chromedriver
    or similar to be installed.

    For each approval test, there are two expected outputs (a.k.a. "baselines"):
      - Vega-Lite spec (in JSON format)
      - SVG image corresponding to Vega-Lite spec

    1. A change to the _image_ (which implies that the Vega Lite also changed) is reported as a test failure.
       To promote to a baseline, move the .new.svg and .new.json files over the corresponding .svg and .json.

    2. Otherwise, the approval test passes. If the Vega Lite has changed, the change is interpreted as a
       refactoring (since it has not visual consequences). This will generate a revised .json file without
       the .new prefix, which can simply be committed as usual.

    When a new approval test is run for the first time, the situation is similar to (1) except that there are
    no preexisting .svg or .json files.

    Some useful `git` aliases are defined in `.gitconfig.aliases` (include the file into your `.gitconfig` to
    enable):

    - `git approve` renames all .new files so that they overwrite the existing baselines (use with care)
    - `git reject` discards all .new files
    """
    if not headless:
        fig.show()

    # easy API call to convert to Vega-Lite; create file later if needed
    ext_vl: str = 'json'
    filename_vl: str = filename + '.' + ext_vl
    have_vl = fig.to_json()

    # go via a file to convert to .svg; keep file around in case needed
    ext_image: str = 'svg'
    filename_new_image: str = filename + '.new.' + ext_image
    fig.save(filename_new_image)
    file_image = open(filename_new_image, 'rb')
    have_image = file_image.read()

    try:
        # load baselines for both Vega-Lite and .svg
        file_vl = open(filename_vl, 'r')
        expected_vl = file_vl.read()
        file_image = open(filename + '.' + ext_image, 'rb')
        expected_image = file_image.read()

        if expected_vl != have_vl:
            print(f"{filename}: Vega-Lite changed.")
            filename_new_vl = filename + '.new.' + ext_vl if expected_image != have_image else filename_vl
            file_new_vl = open(filename_new_vl, 'w')
            file_new_vl.write(have_vl)
        else:
            print(f"{filename}: Vega Lite identical.")

        # require (Vega Lite -> image) to be a function
        assert expected_image == have_image, f"{filename}: image changed."
        print(f"{filename}: image identical.")
        os.remove(filename_new_image)

    except FileNotFoundError as e:
        file_new = open(e.filename, 'w')
        file_new.write(have_vl)
        print(f"{filename}: initial Vega-Lite baseline.")
        assert False, f"{filename}: image not found."


def choropleth_data() -> Any:
    """Dataset for choropleth example."""
    geo_states = gpd.read_file('notebooks/gz_2010_us_040_00_500k.json')
    df_polls = pd.read_csv('notebooks/presidential_poll_averages_2020.csv')
    trump_data = df_polls[df_polls.candidate_name == 'Donald Trump']
    trump_data.columns = [
        'cycle', 'NAME', 'modeldate', 'candidate_name', 'pct_estimate', 'pct_trend_adjusted'
    ]
    geo_states_trump = geo_states.merge(trump_data, on='NAME')
    return geo_states_trump[geo_states_trump.modeldate == '11/03/2020']


@meta_hist
def example_choropleth(candidate_states: pd.DataFrame, title: str, extent: Optional[List[int]]) -> alt.Chart:
    """Choropleth of the US states with the candidate vote percentage mapped to color."""
    color = alt.Color(shorthand='pct_estimate', bin=alt.Bin(maxbins=20), scale=alt.Scale(type='band'))
    chart = alt.Chart(candidate_states, title=title) \
        .mark_geoshape() \
        .encode(color, tooltip=['NAME', 'pct_estimate']) \
        .properties(width=500, height=300) \
        .project(type='albersUsa')

    if extent is not None:
        chart.encoding.color.bin.extent = extent

    return chart


def scatterplot_data() -> Any:
    """Data on movies from IMDB and Rotten Tomatoes."""
    from vega_datasets import data  # type: ignore
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    return pd.read_json(data.movies.url)


@meta_hist
def example_scatterplot(data: pd.DataFrame, color: alt.Color, title: str) -> alt.Chart:
    """Scatterplot of IMdB ratings vs. Rotten Tomatoes by budget."""
    chart = alt.Chart(data, title=title) \
        .mark_circle() \
        .encode(x='IMDB_Rating', y='Rotten_Tomatoes_Rating', color=color)
    return chart


class TestMetaHist:
    """Test the @meta_hist decorator."""

    @staticmethod
    def test_choropleth(headless: bool) -> None:
        chart: alt.Chart = example_choropleth(choropleth_data(), inspect.stack()[0][3], None)
        assert [math.ceil(y) for y in chart.hconcat[0].encoding.y.axis.values] == [0, 6, 50, 62]
        expect_fig(chart, "tests/expected_meta_hist_choropleth", headless)

    @staticmethod
    def test_choropleth_extent(headless: bool) -> None:
        chart: alt.Chart = example_choropleth(choropleth_data(), inspect.stack()[0][3], [0, 100])
        assert [math.ceil(y) for y in chart.hconcat[0].encoding.y.axis.values] == [0, 6, 50, 62]
        expect_fig(chart, "tests/expected_meta_hist_choropleth_extent", headless)

    @staticmethod
    def test_scatterplot_bin_undefined(headless: bool) -> None:
        with pytest.raises(Exception) as e:
            example_scatterplot(scatterplot_data(), 'Production_Budget', inspect.stack()[0][3])
        assert e.value.args[0] == "Can only apply decorator to chart with color.bin defined."

    # In this case "colors used" is an empty plot. See https://github.com/WarwickCIM/ways-py/issues/63.
    @staticmethod
    def test_scatterplot_bin_False(headless: bool) -> None:
        color = alt.Color(shorthand='Production_Budget', bin=False)
        chart: alt.Chart = example_scatterplot(scatterplot_data(), color, inspect.stack()[0][3])
        expect_fig(chart, "tests/expected_meta_hist_scatterplot_bin_False", headless)

    @staticmethod
    def test_scatterplot(headless: bool) -> None:
        scale = alt.Scale(type='band')
        color = alt.Color(shorthand='Production_Budget', bin=alt.Bin(maxbins=20), scale=scale)
        chart: alt.Chart = example_scatterplot(scatterplot_data(), color, inspect.stack()[0][3])
        expect_fig(chart, "tests/expected_meta_hist_scatterplot", headless)
