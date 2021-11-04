from functools import wraps
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
        density_chart = alt.Chart(src.data) \
            .transform_joinaggregate(total='count(*)') \
            .transform_calculate(proportion='1 / datum.total') \
            .mark_bar() \
            .encode(
                alt.Y(
                    src.encoding.color.shorthand,
                    bin=src.encoding.color.bin,
                    axis=alt.Axis(orient='right'),
                    title="",
                ),
                alt.X('sum(proportion):Q', sort='descending', title="density"),
            ) \
            .encode(src.encoding.color) \
            .properties(width=300, height=300)

        colour_bars = alt.Chart(src.data) \
            .mark_bar() \
            .transform_bin(as_=['x', 'x2'], field='pct_estimate') \
            .encode(
                alt.Y(
                    src.encoding.color.shorthand,
                    bin=src.encoding.color.bin,
                    axis=alt.Axis(orient='right'),
                    title="colours",
                ),
                alt.X('count():Q', sort='descending', title=""),
            ) \
            .encode(src.encoding.color) \
            .properties(width=300, height=300)

        return density_chart | colour_bars | src


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def meta_hist(make_chart: FuncT) -> FuncT:
    """Post-compose altair_meta_hist with a function which makes a colour-encoded Altair chart."""
    @wraps(make_chart)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return Ways.altair_meta_hist(make_chart(*args, **kwargs))
    return cast(FuncT, wrapper)
