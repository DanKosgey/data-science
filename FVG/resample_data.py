import pandas as pd
import logging

SUPPORTED_TIMEFRAMES = {
    '1D': '1D',
    '12h': '12H',
    '6h': '6H',
    '4h': '4H',
    '2h': '2H',
    '1h': '1H',
    '30min': '30T',
    '15min': '15T',
    '5min': '5T',
}

def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample OHLCV data to the specified timeframe.
    Returns a new DataFrame or raises ValueError for unsupported timeframes.
    """
    if timeframe not in SUPPORTED_TIMEFRAMES:
        logging.error(f"Unsupported timeframe: {timeframe}")
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    rule = SUPPORTED_TIMEFRAMES[timeframe]
    logging.info(f"Resampling data to {timeframe}...")
    ohlc_dict = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
    }
    resampled = df.resample(rule).apply(ohlc_dict).dropna()
    return resampled

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    # Example usage: load a CSV and resample
    if len(sys.argv) > 1:
        df = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True)
        tf = sys.argv[2] if len(sys.argv) > 2 else '1h'
        resampled = resample_data(df, tf)
        print(resampled.head()) 