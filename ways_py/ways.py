import altair as alt  # type: ignore
import pandas as pd  # type: ignore


class Ways:
    """The WAYS library."""

    def dummy_chart(self) -> alt.Chart:
        df: pd.DataFrame = pd.DataFrame(columns=["x", "y"])
        return alt.Chart(df, title="Dummy Chart").properties(width=600, height=500).mark_point()
