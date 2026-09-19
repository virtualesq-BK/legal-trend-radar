"""Forecasting: Naive, Moving Average, ARIMA, SARIMA compared on a chronological split.

LSTM is explicitly OUT OF SCOPE (see reports/REPORT.md "Limitations" /
"Future Work"). ARIMA/SARIMA are used for stability and reproducibility.

Every model is wrapped defensively: if a model fails to fit (e.g. too few
observations, singular matrix), it is skipped rather than crashing the whole
pipeline or the API.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


@dataclass
class ModelResult:
    name: str
    mae: float
    rmse: float
    mape: float | None
    forecast: pd.Series
    lower_ci: pd.Series | None
    upper_ci: pd.Series | None


def chronological_split(series: pd.Series, val_ratio: float = 0.2) -> tuple[pd.Series, pd.Series]:
    """Split a time-ordered series into train/validation WITHOUT shuffling."""
    n = len(series)
    n_val = max(1, int(n * val_ratio))
    n_train = n - n_val
    return series.iloc[:n_train], series.iloc[n_train:]


def _metrics(actual: pd.Series, pred: pd.Series) -> tuple[float, float, float | None]:
    actual = actual.values.astype(float)
    pred = pred.values.astype(float)
    mae = float(np.mean(np.abs(actual - pred)))
    rmse = float(np.sqrt(np.mean((actual - pred) ** 2)))
    # MAPE is undefined/unstable when actual contains zeros, which is common
    # for low-volume months in this dataset - only compute it when safe.
    if np.all(actual != 0):
        mape = float(np.mean(np.abs((actual - pred) / actual)) * 100)
    else:
        mape = None
    return mae, rmse, mape


def _naive_forecast(train: pd.Series, steps: int) -> pd.Series:
    last = train.iloc[-1]
    return pd.Series([last] * steps)


def _moving_average_forecast(train: pd.Series, steps: int, window: int = 3) -> pd.Series:
    val = train.tail(window).mean()
    return pd.Series([val] * steps)


def _try_arima(train: pd.Series, steps: int, seasonal: bool):
    try:
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        if seasonal and len(train) >= 24:
            model = SARIMAX(
                train,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            fit = model.fit(disp=False)
        else:
            model = ARIMA(train, order=(1, 1, 1))
            fit = model.fit()
        pred = fit.get_forecast(steps=steps)
        mean = pred.predicted_mean
        ci = pred.conf_int(alpha=0.05)
        lower = ci.iloc[:, 0]
        upper = ci.iloc[:, 1]
        return mean.reset_index(drop=True), lower.reset_index(drop=True), upper.reset_index(drop=True)
    except Exception:
        return None, None, None


def evaluate_models(series: pd.Series) -> dict[str, ModelResult]:
    """Fit each candidate model on train, evaluate on validation. Never raises."""
    results: dict[str, ModelResult] = {}
    if len(series) < 6:
        return results
    train, val = chronological_split(series)
    steps = len(val)
    if steps == 0:
        return results

    try:
        pred = _naive_forecast(train, steps)
        mae, rmse, mape = _metrics(val, pred)
        results["naive"] = ModelResult("naive", mae, rmse, mape, pred, None, None)
    except Exception:
        pass

    try:
        pred = _moving_average_forecast(train, steps)
        mae, rmse, mape = _metrics(val, pred)
        results["moving_average"] = ModelResult("moving_average", mae, rmse, mape, pred, None, None)
    except Exception:
        pass

    mean, lower, upper = _try_arima(train, steps, seasonal=False)
    if mean is not None:
        mae, rmse, mape = _metrics(val, mean)
        results["arima"] = ModelResult("arima", mae, rmse, mape, mean, lower, upper)

    mean, lower, upper = _try_arima(train, steps, seasonal=True)
    if mean is not None:
        mae, rmse, mape = _metrics(val, mean)
        results["sarima"] = ModelResult("sarima", mae, rmse, mape, mean, lower, upper)

    return results


def pick_best(results: dict[str, ModelResult]) -> str | None:
    if not results:
        return None
    return min(results, key=lambda k: results[k].rmse)


def forecast_future(series: pd.Series, model_name: str, horizon: int):
    """Refit the chosen model on the FULL series and forecast `horizon` steps ahead."""
    if model_name == "naive":
        pred = _naive_forecast(series, horizon)
        return pred, None, None
    if model_name == "moving_average":
        pred = _moving_average_forecast(series, horizon)
        return pred, None, None
    if model_name in ("arima", "sarima"):
        mean, lower, upper = _try_arima(series, horizon, seasonal=(model_name == "sarima"))
        if mean is not None:
            return mean, lower, upper
    # Fallback: never crash - use naive if the chosen model fails on refit
    pred = _naive_forecast(series, horizon)
    return pred, None, None
