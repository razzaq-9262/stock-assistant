import numpy as np
import pandas as pd

from sandbox.runner import run_code
from tools.calculations import project_value, scenarios
from tools.technical import add_indicators, trend_summary


def _fake_prices(n=120):
    idx = pd.date_range("2026-01-01", periods=n)
    close = pd.Series(np.linspace(100, 150, n), index=idx)
    return pd.DataFrame({"Open": close, "High": close + 1, "Low": close - 1,
                         "Close": close, "Volume": 1000}, index=idx)


def test_project_value_grows():
    df = project_value(1000, 10, 3)
    assert len(df) == 3
    assert df["Value"].iloc[-1] > 1000


def test_scenarios_order():
    df = scenarios(1000, 5)
    assert df["Final value"].is_monotonic_increasing


def test_indicators_and_trend():
    df = add_indicators(_fake_prices())
    summary = trend_summary(df)
    assert summary["trend"] == "uptrend"


def test_sandbox_runs_code():
    assert run_code("print(2 + 2)")["output"].strip() == "4"


def test_sandbox_blocks_dangerous_code():
    assert run_code("import os")["ok"] is False


def test_sandbox_timeout():
    assert run_code("while True: pass", timeout=1)["ok"] is False
