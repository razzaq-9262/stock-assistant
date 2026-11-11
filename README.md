# AI Stock Market Assistant

A conversational assistant that combines market data, technical analysis,
fundamental analysis and Python-powered what-if calculations in one app.

> Educational project. Not financial advice.

## Features
- **Technical analysis**: candlestick chart, SMA20/50, RSI, volume, trend summary
- **Fundamental analysis**: P/E, EPS, margins, market cap, financial statements
- **Calculations**: stock comparison (return, volatility, drawdown), projections, scenarios
- **AI chat**: Claude decides which tool to call (tool calling) and explains the result
- **Sandbox**: model-written Python runs in a separate process with timeout
- **Background jobs**: Celery + Redis for long comparisons, with progress and retries

## Architecture
```
User -> Streamlit UI -> AI Harness (harness.py)
                          |-> Tools (technical / fundamental / calculations) -> Yahoo Finance
                          |-> Python Sandbox (sandbox/runner.py)
                          |-> Redis queue -> Celery workers (worker/tasks.py) -> saved results
```

## Project structure
```
app.py            Streamlit UI
harness.py        AI harness: model + tools + permissions loop
tools/            technical.py, fundamental.py, calculations.py
sandbox/          runner.py (isolated Python execution)
worker/           tasks.py (Celery tasks)
tests/            pytest tests
.github/workflows CI: flake8 + pytest
```

## Run locally
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here     # Windows: set ANTHROPIC_API_KEY=...
streamlit run app.py
```

Background worker (optional):
```bash
redis-server
celery -A worker.tasks worker --loglevel=info
```

Tests and lint:
```bash
pytest -q
flake8 . --max-line-length=100
```

## Team workflow
- Create a branch per feature: `feature/technical-analysis`
- Open a pull request, get one review, CI must pass, then merge to `main`

## Assumptions and limits
- Data comes from Yahoo Finance via `yfinance` (may be delayed).
- Projections assume a constant annual return, which real markets do not give.
- The sandbox here is process-level; production should use Docker/Fargate.
- MCP: market data tools can be wrapped as an MCP server; this demo calls them directly.
