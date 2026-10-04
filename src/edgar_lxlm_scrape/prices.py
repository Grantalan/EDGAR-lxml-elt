"""Download daily stock prices from Yahoo Finance and save them to RustFS."""

import json
from datetime import date

import yfinance as yf

from edgar_lxlm_scrape.extract import already_landed, fetch, land

# OTC stocks mostly have no usable price history, so we skip them.
EXCHANGES = ["Nasdaq", "NYSE", "CBOE"]

# SPY is the market benchmark every strategy gets compared against.
BENCHMARKS = ["SPY"]

# How many tickers to ask Yahoo for at once.
BATCH_SIZE = 100


def get_tickers():
    """Every stock ticker on a major exchange, from SEC's ticker list."""
    data = json.loads(fetch("https://www.sec.gov/files/company_tickers_exchange.json"))
    tickers = [row[2] for row in data["data"] if row[3] in EXCHANGES]
    return sorted(set(tickers)) + BENCHMARKS


def get_prices(tickers, batch_number, period):
    """Daily prices for a batch of tickers, saved as one CSV.

    period="max" is the full history (first run only).
    period="5d" is the last 5 trading days (every run after). The overlap
    covers weekends and missed runs; silver removes the duplicate days.
    """
    df = yf.download(tickers, period=period, group_by="ticker", auto_adjust=False, progress=False, threads=False)

    # Yahoo gives one column group per ticker. Turn that into one row per ticker per day.
    df = df.stack(level=0, future_stack=True).reset_index().dropna(subset=["Close"])

    if period == "max":
        key = f"prices/history/batch_{batch_number:03d}.csv"
    else:
        key = f"prices/daily/{date.today()}/batch_{batch_number:03d}.csv"
    land(key, df.to_csv(index=False).encode())


if __name__ == "__main__":
    # Full history only if we've never downloaded it.
    period = "5d" if already_landed("prices/history/") else "max"

    tickers = get_tickers()
    print(f"{len(tickers)} tickers, period={period}")
    for i in range(0, len(tickers), BATCH_SIZE):
        get_prices(tickers[i : i + BATCH_SIZE], i // BATCH_SIZE, period)
