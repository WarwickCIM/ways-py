import altair as alt  # type: ignore
import pandas as pd  # type: ignore


class Ways:
    """The WAYS library."""

    def dummy_chart(self) -> alt.Chart:
        df: pd.DataFrame = pd.DataFrame(columns=["x", "y"])
        return alt.Chart(df, title="Dummy Chart").properties(width=600, height=500).mark_point()

    def altair_meta_hist(dataframe, column, bin, color):
        """Plot a histogram metavisualisation for a plot with matching
        color binning via same altair objects.

        Args:
        param1 (pd.DataFrame): Dataset to plot.
        param2 (str): Column of the df to visualise.
        param3 (alt.Bin): Pre-configured altair bin object.
        param4 (alt.Color): Pre-configured altair color object.

        Returns:
            altair chart object: histogram
        """
        return alt.Chart(dataframe).mark_bar().encode(
                alt.X(column, bin=bin),
                y='count()',
               ).encode(
                color
               ).properties(
                width=300,
                height=300
               )
