"""Python calculations: comparisons, projections, what-if scenarios."""
import pandas as pd


def compare_stocks(tickers: list, period: str = "1y") -> pd.DataFrame:
    """Compare return, volatility and drawdown of several stocks."""
    import yfinance as yf

    rows = []
    for tk in tickers:
        close = yf.Ticker(tk).history(period=period)["Close"]
        if close.empty:
            continue
        returns = close.pct_change().dropna()
        rows.append({
            "Ticker": tk,
            "Return %": round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2),
            "Volatility %": round(returns.std() * (252 ** 0.5) * 100, 2),
            "Max drawdown %": round(
                ((close / close.cummax()) - 1).min() * 100, 2),
        })
    return pd.DataFrame(rows)


def project_value(amount: float, annual_return_pct: float, years: int,
                  monthly_add: float = 0.0) -> pd.DataFrame:
    """What-if: how an investment grows year by year.

    Assumption: constant annual return, compounded monthly.
    """
    monthly_rate = (1 + annual_return_pct / 100) ** (1 / 12) - 1
    value = amount
    rows = []
    for month in range(1, years * 12 + 1):
        value = value * (1 + monthly_rate) + monthly_add
        if month % 12 == 0:
            rows.append({"Year": month // 12, "Value": round(value, 2)})
    return pd.DataFrame(rows)


def scenarios(amount: float, years: int) -> pd.DataFrame:
    """Pessimistic / base / optimistic scenarios."""
    out = {}
    for name, rate in [("Pessimistic (3%)", 3), ("Base (8%)", 8),
                       ("Optimistic (12%)", 12)]:
        out[name] = project_value(amount, rate, years)["Value"].iloc[-1]
    return pd.DataFrame({"Scenario": list(out), "Final value": list(out.values())})
