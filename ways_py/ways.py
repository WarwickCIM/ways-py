import altair as alt  # type: ignore
import pandas as pd  # type: ignore


class Ways:
    """WAYS library."""

    def dummy_chart(self) -> alt.Chart:
        df: pd.DataFrame = pd.DataFrame(columns=["x", "y"])
        return alt.Chart(df, title="Dummy Chart").properties(width=600, height=500).mark_point()

    @staticmethod
    def altair_meta_hist(src: alt.Chart, column: str) -> alt.Chart:
        """Altair metavisualisation; histogram visualising color bins of another Altair chart.

        Args:
        src: colour-encoded Altair chart underlying the metavisualisation.
        str: column of source chart's data which contains the colour-encoded data.

        Returns:
            altair chart object: histogram
        """
        chart = alt.Chart(src.data) \
            .mark_bar() \
            .encode(alt.Y(column, bin=src.encoding.color.bin), x='count()') \
            .encode(src.encoding.color) \
            .properties(width=300, height=300)
        return chart | src


def meta_hist(make_chart):
    def wrapper(*args, **kwargs):
        return altair_meta_hist(make_chart(*args, **kwargs), 'pct_estimate')
    return wrapper
