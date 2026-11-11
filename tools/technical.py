"""Technical analysis tools: price data, indicators, candlestick chart."""
import pandas as pd


def get_prices(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """Download OHLCV data using yfinance."""
    import yfinance as yf

    df = yf.Ticker(ticker).history(period=period)
    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}'")
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add SMA, RSI and MACD columns."""
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df


def trend_summary(df: pd.DataFrame) -> dict:
    """Return a small dict the AI can explain in plain words."""
    last = df.iloc[-1]
    trend = "uptrend" if last["SMA20"] > last["SMA50"] else "downtrend"
    rsi = float(last["RSI"])
    if rsi > 70:
        rsi_view = "overbought"
    elif rsi < 30:
        rsi_view = "oversold"
    else:
        rsi_view = "neutral"
    return {
        "last_close": round(float(last["Close"]), 2),
        "trend": trend,
        "rsi": round(rsi, 1),
        "rsi_view": rsi_view,
        "avg_volume": int(df["Volume"].tail(20).mean()),
    }


def candlestick_chart(df: pd.DataFrame, ticker: str):
    """Candlestick + SMA lines + volume + RSI in one figure."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03,
    )
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"), row=3, col=1)
    fig.update_layout(title=f"{ticker} - Technical view",
                      xaxis_rangeslider_visible=False, height=700)
    return fig
