from functools import wraps
from typing import Any, Callable, cast, TypeVar

import altair as alt  # type: ignore


class Ways:
    """WAYS library."""

    @staticmethod
    def density_chart(src: alt.Chart) -> alt.Chart:
        return alt.Chart(src.data) \
            .transform_joinaggregate(total='count(*)') \
            .transform_calculate(proportion="1 / datum.total") \
            .mark_bar(color='gray') \
            .encode(
                alt.Y(
                    src.encoding.color.shorthand,
                    bin=alt.Bin(maxbins=50),
                    axis=alt.Axis(orient='left'),
                    title="",
                ),
                alt.X('sum(proportion):Q', sort='descending', title="density"),
            ) \
            .properties(width=100, height=300)


    @staticmethod
    def colour_bars(src: alt.Chart) -> alt.Chart:
        y_axis = alt.Axis(orient='right', grid=False)
        x_axis = alt.Axis(labels=False, tickSize=0, grid=False)
        return alt.Chart(src.data) \
            .mark_rect() \
            .transform_bin(as_=['y', 'y2'], bin=src.encoding.color.bin, field='pct_estimate') \
            .transform_calculate(const='5') \
            .encode(
                y=alt.Y('y:Q', scale={'zero': False}, axis=y_axis, title=""),
                y2='y2:Q',
                x=alt.X('const:Q', sort='descending', axis=x_axis, title=""),
            ) \
            .encode(src.encoding.color) \
            .properties(width=20, height=300)


    @staticmethod
    def altair_meta_hist(src: alt.Chart) -> alt.Chart:
        """Altair metavisualisation; histogram visualising color bins of another Altair chart.

        Args:
        src: colour-encoded Altair chart underlying the metavisualisation.
        str: column of source chart's data which contains the colour-encoded data.

        Returns:
            altair chart object: histogram
        """

        return Ways.density_chart(src) | Ways.colour_bars(src) | src


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def meta_hist(make_chart: FuncT) -> FuncT:
    """Post-compose altair_meta_hist with a function which makes a colour-encoded Altair chart."""
    @wraps(make_chart)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return Ways.altair_meta_hist(make_chart(*args, **kwargs))
    return cast(FuncT, wrapper)
