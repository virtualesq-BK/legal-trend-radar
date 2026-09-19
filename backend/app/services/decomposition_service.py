"""STL decomposition of the monthly count series (trend/seasonal/residual)."""
from __future__ import annotations

import pandas as pd
from statsmodels.tsa.seasonal import STL


class InsufficientDataError(ValueError):
    pass


def run_stl(monthly: pd.DataFrame, period: int = 12, robust: bool = True) -> pd.DataFrame:
    """Run STL on the `count` column. Requires >= 2*period observations.

    Returns a DataFrame with columns: period, observed, trend, seasonal, resid.
    """
    if len(monthly) < 2 * period:
        raise InsufficientDataError(
            f"STL requires at least {2 * period} monthly observations, got {len(monthly)}."
        )
    series = monthly.set_index(pd.PeriodIndex(monthly["period"], freq="M"))["count"].astype(float)
    series.index = series.index.to_timestamp()
    stl = STL(series, period=period, robust=robust)
    result = stl.fit()
    out = pd.DataFrame(
        {
            "period": monthly["period"].values,
            "observed": series.values,
            "trend": result.trend.values,
            "seasonal": result.seasonal.values,
            "resid": result.resid.values,
        }
    )
    return out


def plot_decomposition(decomp: pd.DataFrame, out_path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    for ax, col, title in zip(
        axes,
        ["observed", "trend", "seasonal", "resid"],
        ["Observed", "Trend", "Seasonal", "Residual"],
    ):
        ax.plot(decomp["period"], decomp[col])
        ax.set_title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
