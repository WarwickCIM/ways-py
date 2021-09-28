import altair as alt  # type: ignore
import pandas as pd  # type: ignore


class Ways:
    """WAYS library."""

    def dummy_chart(self) -> alt.Chart:
        df: pd.DataFrame = pd.DataFrame(columns=["x", "y"])
        return alt.Chart(df, title="Dummy Chart").properties(width=600, height=500).mark_point()

    @staticmethod
    def altair_meta_hist(dataframe: pd.DataFrame, column: str, src: alt.Chart) -> alt.Chart:
        """Altair metavisualisation histogram.

        Plot a histogram metavisualisation for a plot with matching
        color binning via same altair objects.

        Args:
        dataframe: dataset to plot.
        str: column of the df to visualise.
        src: colour-encoded Altair chart underlying the metavisualisation.

        Returns:
            altair chart object: histogram
        """
        return alt.Chart(dataframe) \
            .mark_bar() \
            .encode(alt.Y(column, bin=src.encoding.color.bin), x='count()') \
            .encode(src.encoding.color) \
            .properties(width=300, height=300)
