from functools import wraps
from ipywidgets import widgets, HBox, VBox
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


class WAlt:
    """WAYS widgets class for Altair."""

    def __init__(self):
        self.altair_bin_jupyter_widgets()
        self.altair_scale_jupyter_widgets()


    def altair_bin_jupyter_widgets(self) -> dict:
        """Create jupyter widgets with values that can be used as input to alt.Bin objects in a jupyter notebook.

        Returns:
            Dictionary of jupyter widgets and grid with these widgets arranged for display.
        """
        # Checkbox widget that determines whether binning is enabled
        self.bin = widgets.Checkbox(value=True, description='Bin')

        # Textbox accepting integer to select the maximum number of bins
        self.maxbins = widgets.IntText(value=7, description='Max Bins:', continuous_update=True)

        # Two widgets determining where the binning of data starts and ends
        self.extentmin = widgets.IntText(value=0, continuous_update=True, description='Extent Min')
        self.extentmax = widgets.IntText(value=0, continuous_update=True, description='Extent Max')
        self.extent = VBox([self.extentmin, self.extentmax])


        # Grey out extent and maxbins widgets when binning is disabled
        def bin_options(change):
            if change.new:
                self.maxbins.disabled = False
                self.extentmin.disabled = False
                self.extentmax.disabled = False
            else:
                self.maxbins.disabled = True
                self.extentmin.disabled = True
                self.extentmax.disabled = True
        self.bin.observe(bin_options, names='value')

        # Create a horizontal box that contains these widgets
        self.bin_grid = widgets.GridBox([
                                            self.bin,
                                            self.maxbins,
                                            self.extent
                                        ], layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))


    def altair_scale_jupyter_widgets(self) -> dict:
        """Create jupyter widgets with values that can be used as input to alt.Scale objects in a jupyter notebook.

        Returns:
            Dictionary of jupyter widgets and grid with these widgets arranged for display.
        """
        # list of scales from https://altair-viz.github.io/user_guide/generated/core/altair.ScaleType.html#altair.ScaleType
        scales = ['linear', 'log', 'pow', 'sqrt', 'symlog', 'identity', 'sequential', 'time', 'utc', 'quantile', 'quantize', 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band']
        self.scale = widgets.Dropdown(value='linear', options=scales, description = 'Scales')
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
        self.colorschemetype = widgets.RadioButtons(value= 'Scheme', options=['Scheme', 'Range'], description='Color Method')
        self.colorscheme = widgets.Dropdown(options=schemes, description = 'Scheme')

        self.color_1 = widgets.ColorPicker(concise=True, value='red', disabled=True, description='Range')
        self.color_2 = widgets.ColorPicker(concise=True, value='purple', disabled=True)
        self.color_3 = widgets.ColorPicker(concise=True, value='blue', disabled=True)
        color_box = HBox([self.color_1, self.color_2, self.color_3], width=100)
        self.scale_grid = widgets.GridBox([
                                            self.colorschemetype,
                                            self.colorscheme,
                                            color_box,
                                            self.scale
                                            ], layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))

        def choose_coloring_method(change):
            if change.new == 'Scheme':
                self.colorscheme.disabled = False
                self.color_1.disabled = True
                self.color_2.disabled = True
                self.color_3.disabled = True
            elif change.new == 'Range':
                self.colorscheme.disabled = True
                self.color_1.disabled = False
                self.color_2.disabled = False
                self.color_3.disabled = False

        self.colorschemetype.observe(choose_coloring_method, names='value')


    def get_altair_color_obj(self, data, column) -> alt.Color:
        """Build color object for altair plot from widget selections
            Args:
            data: pandas dataframe with the alatir chart data.
            column: column of source chart's data which contains the colour-encoded data.

        Returns:
            alt.Color object to be used by alt.Chart
        """

        # If the bin checkbox selected
        if self.bin.value:
            # If not already set, set the default values of the extent widget to data min and max
            if self.extentmax.value == 0:
                self.extentmin.value = data[column].min()
                self.extentmax.value = data[column].max()
            # create the altair bin object from widget values
            bin = alt.Bin(maxbins=self.maxbins.value, extent=[self.extentmin.value, self.extentmax.value])
        else:
            # set the bin var as False bool which alt.Color accepts
            bin = False
        # Depending on whether scheme or range selected, use different widgets to create the alt.Scale obj
        if self.colorschemetype.value == 'Scheme':
            scale = alt.Scale(type=self.scale.value, scheme=self.colorscheme.value)
        elif self.colorschemetype.value == 'Range':
            colorrange = [
                        self.color_1.value,
                        self.color_2.value,
                        self.color_3.value
                    ]
            scale = alt.Scale(type=self.scale.value, range=colorrange)
        return alt.Color(column, legend=None, bin=bin, scale=scale)


    def display(self, data, column, title, func, custom_widgets=False):
        """Generate interactive plot from widgets and interactive plot function"""

        def interact_func(**kwargs):

            # Use the WAYS widgets to generate the altair color object
            color = self.get_altair_color_obj(data, column)

            # Pass the data, color object and title into the choropleth
            display(func(data, color, title))

        # Get a dictionary of the widgets to be passed to the interactive function
        controls = {
                    'bin': self.bin,
                    'maxbins': self.maxbins,
                    'extentmin': self.extentmin,
                    'extentmax': self.extentmax,
                    'scale': self.scale,
                    'colorschemetype': self.colorschemetype,
                    'colorscheme': self.colorscheme,
                    'color_1': self.color_1,
                    'color_2': self.color_2,
                    'color_3': self.color_3
                    }

        if custom_widgets:
            # Get a dictionary of the widgets to use as controls and add to the dictionary
            controls = custom_widgets | controls

            # Create a GridBox to arrange custom widgets into rows of three
            custom_widgets_grid = widgets.GridBox(list(custom_widgets.values()),
                                                layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))

            # Use Jupyter widgets interactive_output to apply the control widgets to the interactive plot
            display(custom_widgets_grid,
                    self.bin_grid,
                    self.scale_grid,
                    widgets.interactive_output(interact_func, controls))
        else:
            display(self.bin_grid,
                    self.scale_grid,
                    widgets.interactive_output(interact_func, controls))
        # Change the value of a widget so the plot auto-generates
        # Note: for some reason doing this once instead of twice results in duplicate plots...
        # TODO: may have to change this if there are scenarios where bin isn't used
        self.bin.value = False
        self.bin.value = True


def altair_widgets(func):
    def wrapper(data, column, title):
        walt = WAlt()
        walt.display(data, column, title, func)
    return wrapper
