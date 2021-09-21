import altair as alt
import pandas as pd


class Ways:
    """The WAYS library."""

    def dummy_chart(self) -> alt.Chart:
        df: pd.DataFrame = pd.DataFrame(columns=["x", "y"])
        return alt.Chart(df, title="Mean Control Chart").properties(width=600, height=500)
