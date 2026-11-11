"""Fundamental analysis tools: company info, financials, valuation."""
import pandas as pd


def get_fundamentals(ticker: str) -> dict:
    """Key valuation and performance numbers from yfinance."""
    import yfinance as yf

    info = yf.Ticker(ticker).info
    keys = {
        "name": "longName",
        "sector": "sector",
        "market_cap": "marketCap",
        "pe_ratio": "trailingPE",
        "forward_pe": "forwardPE",
        "eps": "trailingEps",
        "profit_margin": "profitMargins",
        "revenue": "totalRevenue",
        "debt_to_equity": "debtToEquity",
        "dividend_yield": "dividendYield",
    }
    return {label: info.get(k) for label, k in keys.items()}


def get_financial_statements(ticker: str) -> dict:
    """Income statement, balance sheet and cash flow as DataFrames."""
    import yfinance as yf

    t = yf.Ticker(ticker)
    return {
        "income": t.financials,
        "balance_sheet": t.balance_sheet,
        "cash_flow": t.cashflow,
    }


def fundamentals_table(data: dict) -> pd.DataFrame:
    """Turn the fundamentals dict into a clean two-column table."""
    return pd.DataFrame(
        {"Metric": list(data.keys()), "Value": list(data.values())}
    )
