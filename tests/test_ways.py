"""Test module for backfillz."""

import errno
import inspect
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


# Plotly doesn't generate SVG deterministically; use PNG instead.
def expect_fig(fig: alt.Chart, filename: str, headless: bool) -> None:
    """Check for JSON-equivalence to stored image."""
    have_vl = fig.to_json()

    ext_vl: str = 'json'
    ext_image: str = 'svg'
    new_filename_image: str = filename + '.new.' + ext_image
    fig.save(new_filename_image)
    file_image = open(new_filename_image, 'rb')
    have_image = file_image.read()

    try:
        # Garbage collect any existing .new files
        new_filename_vl: str = filename + '.new.' + ext_vl
        if os.path.isfile(new_filename_vl):
            os.remove(new_filename_vl)

        file_vl = open(filename + '.' + ext_vl, 'r')
        expected_vl = file_vl.read()

        if expected_vl != have_vl:
            print(f"{filename}: differs from baseline Vega Lite.")

            file_image = open(filename + '.' + ext_image, 'rb')
            expected_image = file_image.read()

            if expected_image != have_image:
                print(f"{filename}: differs from baseline image.")
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), new_filename_vl)
        else:
            print(f"{filename}: Vega Lite identical.")
            # therefore: image identical

        print(f"{filename}: image identical.")
        os.remove(new_filename_image)

        if not headless:
            fig.show()
    except FileNotFoundError as e:
        file_new = open(e.filename, 'w')
        file_new.write(have_vl)
        print(f"{filename}: creating new Vega Lite baseline.")
        alt.renderers.enable('mimetype')  # not sure what this is for
        if not headless:
            fig.show()
        assert False, f"{filename}: Vega Lite changed."


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
        """Altair meta-visualisation generates without error."""
        chart: alt.Chart = example_choropleth(choropleth_data(), inspect.stack()[0][3], None)
        expect_fig(chart, "tests/expected_meta_hist_choropleth", headless)

    @staticmethod
    def test_choropleth_extent(headless: bool) -> None:
        """Altair meta-visualisation generates without error."""
        chart: alt.Chart = example_choropleth(choropleth_data(), inspect.stack()[0][3], [0, 100])
        expect_fig(chart, "tests/expected_meta_hist_choropleth_extent", headless)

    @staticmethod
    def test_scatterplot_bin_undefined(headless: bool) -> None:
        """Altair meta-visualisation generates with error."""
        with pytest.raises(Exception) as e:
            example_scatterplot(scatterplot_data(), 'Production_Budget', inspect.stack()[0][3])
        assert e.value.args[0] == "Can only apply decorator to chart with color.bin defined."

    # In this case "colors used" is an empty plot. See https://github.com/WarwickCIM/ways-py/issues/63.
    @staticmethod
    def test_scatterplot_bin_False(headless: bool) -> None:
        """Altair meta-visualisation generates without error."""
        color = alt.Color(shorthand='Production_Budget', bin=False)
        chart: alt.Chart = example_scatterplot(scatterplot_data(), color, inspect.stack()[0][3])
        expect_fig(chart, "tests/expected_meta_hist_scatterplot_bin_False", headless)

    @staticmethod
    def test_scatterplot(headless: bool) -> None:
        """Altair meta-visualisation generates without error."""
        scale = alt.Scale(type='band')
        color = alt.Color(shorthand='Production_Budget', bin=alt.Bin(maxbins=20), scale=scale)
        chart: alt.Chart = example_scatterplot(scatterplot_data(), color, inspect.stack()[0][3])
        expect_fig(chart, "tests/expected_meta_hist_scatterplot", headless)
