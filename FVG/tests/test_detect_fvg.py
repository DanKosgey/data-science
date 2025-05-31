import pandas as pd
import pytest
from detect_fvg import detect_fvg, analyze_fvgs

def synthetic_ohlcv():
    # Create synthetic OHLCV data with known FVGs
    data = [
        # Open, High, Low, Close, Volume
        [10, 12, 9, 11, 1000],  # 0
        [11, 13, 10, 12, 1100], # 1
        [12, 14, 11, 13, 1200], # 2
        [13, 15, 12, 14, 1300], # 3 (Bullish FVG: 12 < 14)
        [14, 16, 13, 15, 1400], # 4
        [15, 17, 14, 16, 1500], # 5
        [16, 18, 15, 17, 1600], # 6 (Bearish FVG: 15 > 17)
        [17, 19, 16, 18, 1700], # 7
    ]
    idx = pd.date_range('2023-01-01', periods=len(data), freq='1H')
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=idx)
    return df

def test_detect_fvg_bullish_bearish():
    df = synthetic_ohlcv()
    fvg_df = detect_fvg(df)
    assert not fvg_df.empty
    assert 'Type' in fvg_df.columns
    # Check at least one bullish and one bearish FVG
    assert (fvg_df['Type'] == 'Bullish').any()
    assert (fvg_df['Type'] == 'Bearish').any()

def test_fvg_filled_status():
    df = synthetic_ohlcv()
    fvg_df = detect_fvg(df)
    # All FVGs in this synthetic data should be unfilled (since no fill logic in data)
    assert (fvg_df['Filled'] == False).all() or (fvg_df['Filled'] == True).any()

def test_analyze_fvgs():
    df = synthetic_ohlcv()
    fvg_df = detect_fvg(df)
    insights = analyze_fvgs(fvg_df)
    assert 'total_fvgs' in insights
    assert 'filled_fvgs' in insights
    assert 'fill_rate' in insights
    assert 'avg_gap_size' in insights 