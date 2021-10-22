from functools import wraps
from ipywidgets import HBox, widgets
from typing import Any, Callable, cast, TypeVar

import altair as alt  # type: ignore


class Ways:
    """WAYS library."""

    @staticmethod
    def altair_meta_hist(src: alt.Chart) -> alt.Chart:
        """Altair metavisualisation; histogram visualising color bins of another Altair chart.

        Args:
        src: colour-encoded Altair chart underlying the metavisualisation.
        str: column of source chart's data which contains the colour-encoded data.

        Returns:
            altair chart object: histogram
        """
        chart = alt.Chart(src.data) \
            .mark_bar() \
            .encode(alt.Y(src.encoding.color.shorthand, bin=src.encoding.color.bin), x='count()') \
            .encode(src.encoding.color) \
            .properties(width=300, height=300)
        return chart | src


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def meta_hist(make_chart: FuncT) -> FuncT:
    """Post-compose altair_meta_hist with a function which makes a colour-encoded Altair chart."""
    @wraps(make_chart)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return Ways.altair_meta_hist(make_chart(*args, **kwargs))
    return cast(FuncT, wrapper)


def altair_bin_jupyter_widgets():
    # Checkbox that determines whether we use color binning - if false, color scheme is continuous
    bin = widgets.Checkbox(value=True, description='Bin')

    # Select the maximum number of bins
    maxbins = widgets.IntSlider(value=100, min=2, max=100, step=1, description='Max Bins', continuous_update=False)

    # Double-slider: Choose the extent of the polling percentage data to plot
    extent = widgets.IntRangeSlider(value=[0,100], min=0, max=100, description='Extent', continuous_update=False)

    # Grey out the widgets that work with the Bin object when bin not selected
    def bin_options(change):
        if change.new:
            maxbins.disabled = False
            extent.disabled = False
        else:
            maxbins.disabled = True
            extent.disabled = True
    bin.observe(bin_options, names='value')

    bin_grid = HBox([bin, maxbins, extent], width=300)

    return {'bin': bin,
            'maxbins': maxbins,
            'extent': extent,
            'bin_grid': bin_grid
           }


def altair_scale_jupyter_widget():
    # list from https://altair-viz.github.io/user_guide/generated/core/altair.ScaleType.html#altair.ScaleType
    scales = ['linear', 'log', 'pow', 'sqrt', 'symlog', 'identity', 'sequential', 'time', 'utc', 'quantile', 'quantize', 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band']
    return widgets.Dropdown(value='linear', options=scales, description = 'Scales')


def altair_color_jupyter_widgets():
    # list from https://vega.github.io/vega/docs/schemes/#reference
    schemes = ['blues', 'tealblues', 'teals', 'greens', 'browns', 'oranges', 'reds', 'purples', 'warmgreys', 'greys',
           'viridis', 'magma', 'inferno', 'plasma', 'cividis', 'turbo', 'bluegreen', 'bluepurple', 'goldgreen',
           'goldorange', 'goldred', 'greenblue', 'orangered', 'purplebluegreen', 'purpleblue', 'purplered',
           'redpurple', 'yellowgreenblue', 'yellowgreen', 'yelloworangebrown', 'yelloworangered', 'darkblue',
           'darkgold','darkgreen','darkmulti','darkred', 'lightgreyred', 'lightgreyteal', 'lightmulti', 'lightorange',
           'lighttealblue', 'blueorange', 'brownbluegreen', 'purplegreen', 'pinkyellowgreen', 'purpleorange',
           'redblue', 'redgrey', 'redyellowblue', 'redyellowgreen', 'spectral', 'rainbow', 'sinebow']
    # The widgets here expose a variety of options for setting the color scheme:
    # colorscheme and the color range boxes are greyed out when not selected by colorschemetype
    colorschemetype = widgets.RadioButtons(value= 'Scheme', options=['Scheme', 'Range'], description='Color Method')
    colorscheme = widgets.Dropdown(options=schemes, description = 'Scheme')

    color_1 = widgets.ColorPicker(concise=True, value='red', disabled=True, description='Range')
    color_2 = widgets.ColorPicker(concise=True, value='purple', disabled=True)
    color_3 = widgets.ColorPicker(concise=True, value='blue', disabled=True)
    color_box = HBox([color_1, color_2, color_3], width=100)
    color_grid = HBox([colorschemetype, colorscheme, color_box], width=300)

    def choose_coloring_method(change):
        if change.new == 'Scheme':
            colorscheme.disabled = False
            color_1.disabled = True
            color_2.disabled = True
            color_3.disabled = True
        elif change.new == 'Range':
            colorscheme.disabled = True
            color_1.disabled = False
            color_2.disabled = False
            color_3.disabled = False

    colorschemetype.observe(choose_coloring_method, names='value')

    return {
        'colorschemetype': colorschemetype,
        'colorscheme': colorscheme,
        'color_1': color_1,
        'color_2': color_2,
        'color_3': color_3,
        'color_grid': color_grid
    }


def get_altair_color_obj(bin, maxbins, scale, extent, colorschemetype, colorscheme,
                  color_1, color_2, color_3, column):
    """Build color object for altair plot from widget selections"""
    if bin: # if bin is False, leave as bool
        bin = alt.Bin(maxbins=maxbins, extent=extent)
    if colorschemetype == 'Scheme':
        scale = alt.Scale(type=scale, scheme=colorscheme)
    elif colorschemetype == 'Range':
        scale = alt.Scale(type=scale, range=[color_1, color_2, color_3])
    color = alt.Color(column,
                      legend=None,
                      bin=bin,
                      scale=scale
                     )
    return color
