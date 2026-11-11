"""Celery worker for long analyses (e.g. comparing many stocks).

Run Redis, then:  celery -A worker.tasks worker --loglevel=info
"""
import os

from celery import Celery

BROKER = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("stock_tasks", broker=BROKER, backend=BROKER)


@app.task(bind=True, max_retries=3, default_retry_delay=5)
def compare_task(self, tickers, period="1y"):
    """Compare stocks in the background with progress and retries."""
    from tools.calculations import compare_stocks

    try:
        self.update_state(state="PROGRESS", meta={"step": "Downloading data"})
        df = compare_stocks(tickers, period)
        self.update_state(state="PROGRESS", meta={"step": "Building table"})
        return df.to_dict(orient="records")
    except Exception as exc:
        raise self.retry(exc=exc)
