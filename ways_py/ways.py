from functools import wraps
from typing import Any, Callable, cast, TypeVar

import altair as alt  # type: ignore
from IPython.display import display  # type: ignore
from ipywidgets import Box, Layout, widgets  # type: ignore
import pandas as pd  # type: ignore
import traitlets  # type: ignore


def is_defined(v: Any) -> bool:
    """Altair's notion of an undefined schema property."""
    return type(v).__name__ != 'UndefinedType'


class Ways:
    """WAYS library."""

    # Centralise the assumption that this property stores just a field name.
    @staticmethod
    def field(src: alt.Chart) -> str:
        return cast(str, src.encoding.color.shorthand)

    @staticmethod
    def density_chart(src: alt.Chart) -> alt.Chart:
        if src.encoding.color.bin and is_defined(src.encoding.color.bin.extent):
            extent = src.encoding.color.bin.extent
            bin = alt.Bin(maxbins=100, extent=extent)
            y_scale = alt.Scale(domain=extent, nice=True)
        else:
            bin = alt.Bin(maxbins=100)
            y_scale = alt.Scale(zero=False, nice=True)
        ys = src.data[Ways.field(src)]  # assume src.data array-like in an appropriate way
        y_min, y_max = min(ys), max(ys)
        # tickCount/tickMinStep Axis properties are ignored (perhaps because we specify bins), so hard code
        y_axis = alt.Y(
            src.encoding.color.shorthand,
            bin=bin,
            axis=alt.Axis(orient='left', grid=False, values=sorted([0, 50] + [y_min, y_max])),
            title="",
            scale=y_scale
        )
        x_axis = alt.X(
            'sum(proportion):Q',
            sort='descending',
            axis=alt.Axis(grid=False),
            title="density"
        )
        return alt.Chart(src.data) \
            .transform_joinaggregate(total='count(*)') \
            .transform_calculate(proportion="1 / datum.total") \
            .mark_bar(color='gray') \
            .encode(y_axis, x_axis) \
            .properties(width=100, height=300)

    @staticmethod
    def used_colours(src: alt.Chart) -> alt.Chart:
        y_axis = alt.Axis(orient='right', grid=False)
        x_axis = alt.Axis(labels=False, tickSize=0, grid=False, titleAngle=270, titleAlign='right')
        if src.encoding.color.bin and is_defined(src.encoding.color.bin.extent):
            extent = src.encoding.color.bin.extent
            y_scale = alt.Scale(domain=extent, nice=True)
        else:
            y_scale = alt.Scale(zero=False, nice=True)
        if src.encoding.color.bin:
            chart = alt.Chart(src.data) \
                .mark_rect() \
                .transform_bin(as_=['y', 'y2'], bin=src.encoding.color.bin, field=Ways.field(src)) \
                .transform_calculate(x='5') \
                .encode(
                    y=alt.Y('y:Q', axis=y_axis, title="", scale=y_scale),
                    y2='y2:Q',
                    x=alt.X('x:Q', sort='descending', axis=x_axis, title="colours used")
                )  # noqa: E123
        else:
            # The following (which happens when bin=False) doesn't make sense; in particular y and y2 are
            # not defined, so it doesn't make sense to try and plot them.
            chart = alt.Chart(src.data) \
                .mark_rect() \
                .transform_calculate(x='5') \
                .encode(
                    y=alt.Y('y:Q', axis=y_axis, title=""),
                    y2='y2:Q',
                    x=alt.X('x:Q', sort='descending', axis=x_axis, title="colours used")
                )  # noqa: E123

        return chart \
            .encode(src.encoding.color) \
            .properties(width=20, height=300)  # noqa: E123

    @staticmethod
    def altair_meta_hist(src: alt.Chart) -> alt.Chart:
        """Decorate an Altair chart with colour binning, with metavisualisations showing the binning profile.

        Args:
        src: colour-encoded Altair chart to be decorated.

        Returns:
            Altair chart object: modified chart
        """
        if not is_defined(src.encoding.color.bin):
            raise Exception("Can only apply decorator to chart with color.bin defined.")

        meta_chart: alt.Chart = (Ways.density_chart(src) | Ways.used_colours(src))
        return (meta_chart | src) \
            .configure_view(strokeWidth=0) \
            .configure_concat(spacing=5)


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def meta_hist(make_chart: FuncT) -> FuncT:
    """Post-compose altair_meta_hist with a function which makes a colour-encoded Altair chart."""
    @wraps(make_chart)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return Ways.altair_meta_hist(make_chart(*args, **kwargs))
    return cast(FuncT, wrapper)


class WAlt:
    """WAYS widgets class for Altair."""

    def __init__(self) -> None:
        """Create jupyter widgets that can be used as input to altair objects in a jupyter notebook."""
        # Checkbox widget that determines whether binning is enabled
        self.bin = widgets.RadioButtons(value='Binned',
                                        options=['Binned', 'Continuous'],
                                        description='Color Binning')

        # Textbox accepting integer to select the maximum number of bins
        self.maxbins = widgets.IntText(value=7, description='Max Bins:', continuous_update=True)

        # Two widgets determining where the binning of data starts and ends
        self.extentmin = widgets.IntText(value=0, continuous_update=True, description='Extent Min')
        self.extentmax = widgets.IntText(value=0, continuous_update=True, description='Extent Max')
        wide_Vbox = Layout(display='flex', flex_flow='column', align_items='center', width='110%')
        self.extent = Box(children=[self.extentmin, self.extentmax], layout=wide_Vbox)

        # Create a horizontal box that contains these widgets
        self.bin_grid = widgets.GridBox([self.bin,
                                         self.maxbins,
                                         self.extent],
                                        layout=Layout(
                                            grid_template_columns="repeat(3, 300px)")
                                        )

        # list of scales from:
        # https://altair-viz.github.io/user_guide/generated/core/altair.ScaleType.html#altair.ScaleType
        scales = ['linear', 'log', 'pow', 'sqrt', 'symlog', 'identity', 'sequential', 'time', 'utc',
                  'quantile', 'quantize', 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band']
        self.scale = widgets.Dropdown(value='linear', options=scales, description='Color Scale')
        # list from https://vega.github.io/vega/docs/schemes/#reference
        schemes = ['blues', 'tealblues', 'teals', 'greens', 'browns', 'oranges', 'reds', 'purples',
                   'warmgreys', 'greys', 'viridis', 'magma', 'inferno', 'plasma', 'cividis', 'turbo',
                   'bluegreen', 'bluepurple', 'goldgreen', 'goldorange', 'goldred', 'greenblue',
                   'orangered', 'purplebluegreen', 'purpleblue', 'purplered', 'redpurple',
                   'yellowgreenblue', 'yellowgreen', 'yelloworangebrown', 'yelloworangered',
                   'darkblue', 'darkgold', 'darkgreen', 'darkmulti', 'darkred', 'lightgreyred',
                   'lightgreyteal', 'lightmulti', 'lightorange', 'lighttealblue', 'blueorange',
                   'brownbluegreen', 'purplegreen', 'pinkyellowgreen', 'purpleorange', 'redblue',
                   'redgrey', 'redyellowblue', 'redyellowgreen', 'spectral', 'rainbow', 'sinebow']
        # The widgets here expose a variety of options for setting the color scheme:
        # colorscheme and the color range boxes are greyed out when not selected by colorschemetype
        self.colorschemetype = widgets.RadioButtons(value='Scheme',
                                                    options=['Scheme', 'Range'],
                                                    description='Color Method')
        self.colorscheme = widgets.Dropdown(options=schemes, description='Scheme')

        self.color_1 = widgets.ColorPicker(concise=True, value='red', disabled=True, description='Range')
        self.color_2 = widgets.ColorPicker(concise=True, value='purple', disabled=True)
        self.color_3 = widgets.ColorPicker(concise=True, value='blue', disabled=True)
        wide_Hbox = Layout(display='flex', flex_flow='row', align_items='center', width='110%')
        color_box = Box([self.color_1, self.color_2, self.color_3], layout=wide_Hbox)
        self.scale_grid = widgets.GridBox([self.colorschemetype,
                                           self.colorscheme,
                                           color_box,
                                           self.scale],
                                          layout=Layout(
                                              grid_template_columns="repeat(3, 300px)")
                                          )

        def choose_coloring_method(change: traitlets.utils.bunch.Bunch) -> None:
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

        # Grey out extent and maxbins widgets when binning is disabled
        def bin_options(change: traitlets.utils.bunch.Bunch) -> None:
            if change.new == 'Binned':
                self.maxbins.disabled = False
                self.extentmin.disabled = False
                self.extentmax.disabled = False
                self.scale.disabled = True
                self.colorschemetype.value = 'Scheme'
                self.colorschemetype.disabled = True
            else:
                self.maxbins.disabled = True
                self.extentmin.disabled = True
                self.extentmax.disabled = True
                self.scale.disabled = False
                self.colorschemetype.disabled = False

        self.bin.observe(bin_options, names='value')

    def get_altair_color_obj(self, data: pd.DataFrame, column: str) -> alt.Color:
        """Build color object for altair plot from widget selections.

            Args:
            data: pandas dataframe with the alatir chart data.
            column: column of source chart's data which contains the colour-encoded data.

        Returns:
            alt.Color object to be used by alt.Chart
        """
        # If the bin checkbox selected
        if self.bin.value == 'Binned':
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
            # Only use the scale widget when bin not selected
            # (otherwise binning colour scale ignored in favour of continuous scale)
            if self.bin.value == 'Binned':
                scale = alt.Scale(scheme=self.colorscheme.value)
            else:
                scale = alt.Scale(type=self.scale.value, scheme=self.colorscheme.value)
        elif self.colorschemetype.value == 'Range':
            colorrange = [self.color_1.value,
                          self.color_2.value,
                          self.color_3.value
                          ]
            # The below only looks right when bin is false (continuous scale).
            # Widgets have been set up so that self.colorschemetype.value is always 'Scheme'
            # when self.bin.value is 'Binned'.
            scale = alt.Scale(type=self.scale.value, range=colorrange)
        return alt.Color(column, legend=None, bin=bin, scale=scale)

    def display(self, data: pd.DataFrame, column: str, func: FuncT,
                custom_widgets: dict[str, Any] = {}) -> None:
        """Generate interactive plot from widgets and interactive plot function.

        Args:
        data: pandas df.
        column: column of data to be used for color binning.
        func: chart plotting function.
        custom_widgets: dictionary of string name keys and widget values.
        """
        def interact_func(**kwargs: Any) -> None:
            """Interactive function that gets passed to widgets.interactive_output."""
            # Use the WAYS widgets to generate the altair color object
            color = self.get_altair_color_obj(data, column)

            # Pass the data and color object into the chart func
            display(func(data, color))

        # Get a dictionary of the widgets to be passed to the interactive function
        controls = {'bin': self.bin,
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
                                                  layout=Layout(grid_template_columns="repeat(3, 300px)")
                                                  )

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
        self.bin.value = 'Continuous'
        self.bin.value = 'Binned'


def altair_widgets(custom_widgets: dict[str, Any] = {}) -> Callable[[FuncT], Callable[[Any, str], None]]:
    """Widgets decorator for altair color binning with option to add custom widgets.

    Args:
    custom_widgets: dictionary of string name keys and widget values.
    """
    def decorator(func: FuncT) -> Callable[[Any, str], None]:
        def wrapper(data: pd.DataFrame, column: str) -> None:
            if custom_widgets:
                # Add each custom widget to the WAlt class
                for name, widget in custom_widgets.items():
                    setattr(WAlt, name, widget)
            walt = WAlt()
            walt.display(data, column, func, custom_widgets=custom_widgets)
        return wrapper
    return decorator
