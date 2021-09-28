import altair as alt  # type: ignore
import pandas as pd  # type: ignore


class Ways:
    """WAYS library."""

    def dummy_chart(self) -> alt.Chart:
        df: pd.DataFrame = pd.DataFrame(columns=["x", "y"])
        return alt.Chart(df, title="Dummy Chart").properties(width=600, height=500).mark_point()

    @staticmethod
    def altair_meta_hist(dataframe: pd.DataFrame, column: str, bin: alt.Bin, color: alt.Color) -> alt.Chart:
        """Altair metavisualisation histogram.

        Plot a histogram metavisualisation for a plot with matching
        color binning via same altair objects.

        Args:
        dataframe: Dataset to plot.
        str: Column of the df to visualise.
        bin: Pre-configured altair bin object.
        color: Pre-configured altair color object.

        Returns:
            altair chart object: histogram
        """
        return alt.Chart(dataframe) \
            .mark_bar() \
            .encode(alt.X(column, bin=bin), y='count()') \
            .encode(color) \
            .properties(width=300, height=300)
