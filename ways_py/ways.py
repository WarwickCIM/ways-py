from functools import wraps
from typing import Any, Callable, cast, TypeVar

import altair as alt  # type: ignore


class Ways:
    """WAYS library."""

    # Centralise the assumption that this property stores just a field name.
    @staticmethod
    def field(src: alt.Chart) -> str:
        return cast(str, src.encoding.color.shorthand)

    @staticmethod
    def density_chart(src: alt.Chart) -> alt.Chart:
        ys = src.data[Ways.field(src)]  # assume src.data array-like in an appropriate way
        y_min, y_max = min(ys), max(ys)
        # tickCount/tickMinStep Axis properties are ignored (because we specify bins?), so hardcode for now
        y_axis = alt.Y(
            src.encoding.color.shorthand,
            bin=alt.Bin(maxbins=100),
            axis=alt.Axis(orient='left', grid=False, values=sorted([0, 50] + [y_min, y_max])),
            title="",
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
        return alt.Chart(src.data) \
            .mark_rect() \
            .transform_bin(as_=['y', 'y2'], bin=src.encoding.color.bin, field=Ways.field(src)) \
            .transform_calculate(x='5') \
            .encode(
                y=alt.Y('y:Q', scale=alt.Scale(zero=False), axis=y_axis, title=""),
                y2='y2:Q',
                x=alt.X('x:Q', sort='descending', axis=x_axis, title="colours used")
            ) \
            .encode(src.encoding.color) \
            .properties(width=20, height=300)  # noqa: E123

    @staticmethod
    def altair_meta_hist(src: alt.Chart) -> alt.Chart:
        """Decorate an Altair chart with histogram metavisualisation showing color binning.

        Args:
        src: colour-encoded Altair chart to be decorated.

        Returns:
            Altair chart object: modified chart
        """
        meta_chart: alt.Chart = (Ways.density_chart(src) | Ways.used_colours(src)).resolve_scale(y='shared')
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
