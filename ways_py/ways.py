from functools import wraps
from ipywidgets import widgets, HBox
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
    """Create jupyter widgets with values that can be used as input to alt.Bin objects in a jupyter notebook.

    Returns:
        Dictionary of jupyter widgets and grid with these widgets arranged for display.
    """
    # Checkbox widget that determines whether binning is enabled
    bin = widgets.Checkbox(value=True, description='Bin')

    # Slider to select the maximum number of bins
    maxbins = widgets.IntSlider(value=100, min=2, max=100, step=1, description='Max Bins', continuous_update=False)

    # Double-slider: Determines where the binning of data starts and ends
    extent = widgets.IntRangeSlider(value=[0,100], min=0, max=100, description='Extent', continuous_update=False)

    # Grey out extent and maxbins widgets when binning is disabled
    def bin_options(change):
        if change.new:
            maxbins.disabled = False
            extent.disabled = False
        else:
            maxbins.disabled = True
            extent.disabled = True
    bin.observe(bin_options, names='value')

    # Create a horizontal box that contains these widgets
    bin_grid = widgets.GridBox([bin, maxbins, extent], layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))

    return {'bin': bin,
            'maxbins': maxbins,
            'extent': extent,
            'bin_grid': bin_grid
           }


def altair_scale_jupyter_widgets():
    """Create jupyter widgets with values that can be used as input to alt.Scale objects in a jupyter notebook.

    Returns:
        Dictionary of jupyter widgets and grid with these widgets arranged for display.
    """
    # list of scales from https://altair-viz.github.io/user_guide/generated/core/altair.ScaleType.html#altair.ScaleType
    scales = ['linear', 'log', 'pow', 'sqrt', 'symlog', 'identity', 'sequential', 'time', 'utc', 'quantile', 'quantize', 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band']
    scale_dropdown =  widgets.Dropdown(value='linear', options=scales, description = 'Scales')
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
    scale_grid = widgets.GridBox([colorschemetype, colorscheme, color_box, scale_dropdown], layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))

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
        'scale': scale_dropdown,
        'colorschemetype': colorschemetype,
        'colorscheme': colorscheme,
        'color_1': color_1,
        'color_2': color_2,
        'color_3': color_3,
        'scale_grid': scale_grid
    }


def get_altair_color_obj(bin, maxbins, scale, extent, colorschemetype, colorscheme, colorrange, column):
    """Build color object for altair plot from widget selections"""
    if bin: # if bin is False, leave as bool
        bin = alt.Bin(maxbins=maxbins, extent=extent)
    if colorschemetype == 'Scheme':
        scale = alt.Scale(type=scale, scheme=colorscheme)
    elif colorschemetype == 'Range':
        scale = alt.Scale(type=scale, range=colorrange)
    color = alt.Color(column,
                      legend=None,
                      bin=bin,
                      scale=scale
                     )
    return color
