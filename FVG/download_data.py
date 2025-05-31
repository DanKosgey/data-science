import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
import time
from typing import List

MAX_LOOKBACK_DAYS = 30   # Yahoo only serves 1m data for the last 30 days
MAX_CHUNK_DAYS    = 7    # and at most 7 days per request

def chunk_date_range(start: datetime, end: datetime, delta: timedelta) -> List[tuple]:
    current = start
    while current < end:
        next_end = min(current + delta, end)
        yield current, next_end
        current = next_end

def download_data(
    ticker: str,
    start: str,
    end: str,
    interval: str = '1m',
    retries: int = 3,
    pause: float = 1.0,
    auto_adjust: bool = False
) -> pd.DataFrame:
    logging.info(f"Requested {ticker}: {start} → {end} @ {interval}")

    now = datetime.utcnow()
    start_dt = datetime.fromisoformat(start)
    end_dt   = datetime.fromisoformat(end)

    earliest = now - timedelta(days=MAX_LOOKBACK_DAYS)
    if start_dt < earliest:
        logging.warning(
            f"Start {start_dt.date()} is older than {MAX_LOOKBACK_DAYS} days; "
            f"clipping to {earliest.date()}"
        )
        start_dt = earliest

    if start_dt >= end_dt:
        logging.error("After clipping, start ≥ end → no data to download.")
        return pd.DataFrame()

    frames = []
    chunk_delta = timedelta(days=MAX_CHUNK_DAYS)

    for idx, (s, e) in enumerate(chunk_date_range(start_dt, end_dt, chunk_delta), start=1):
        logging.info(f"  Chunk {idx}: {s.date()} → {e.date()}")
        for attempt in range(1, retries+1):
            try:
                df = yf.download(
                    tickers=ticker,
                    start=s.strftime("%Y-%m-%d"),
                    end=e.strftime("%Y-%m-%d"),
                    interval=interval,
                    auto_adjust=auto_adjust,
                    progress=False
                )
                if df.empty:
                    logging.warning(f"    → No data returned for chunk {idx}.")
                else:
                    frames.append(df.dropna())
                break
            except Exception as ex:
                msg = str(ex)
                if "YFPricesMissingError" in msg or "no price data found" in msg:
                    logging.error(f"    → Permanent error (no data): {msg}")
                    break
                logging.error(f"    → Chunk {idx}, attempt {attempt} failed: {msg}")
                if attempt < retries:
                    time.sleep(pause * attempt)
                else:
                    logging.error(f"    → Giving up on chunk {idx}.")
        time.sleep(pause)

    if not frames:
        logging.warning("No data downloaded for any chunk.")
        return pd.DataFrame()

    df_all = pd.concat(frames)
    df_all = df_all[~df_all.index.duplicated(keep='first')]
    df_all.sort_index(inplace=True)
    logging.info(f"Successfully downloaded {len(df_all)} rows.")
    return df_all

if __name__ == "__main__":
    import sys
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    start  = sys.argv[2] if len(sys.argv) > 2 else "2023-01-01"
    end    = sys.argv[3] if len(sys.argv) > 3 else datetime.utcnow().date().isoformat()

    df = download_data(ticker, start, end)
    if df.empty:
        print("No data downloaded.")
    else:
        print(df.head())
        print(df.tail())
