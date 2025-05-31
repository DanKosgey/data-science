import pandas as pd
import logging
from typing import Optional

def detect_fvg(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all historical bullish and bearish FVGs in the OHLCV DataFrame.
    Returns a DataFrame with columns: ['Timestamp', 'Type', 'Gap_Low', 'Gap_High', 'Filled', 'Fill_Time']
    """
    results = []
    for i in range(2, len(df)):
        n2, n1, n = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        ts = df.index[i]
        # Bullish FVG
        if n2['High'] < n['Low']:
            gap_low, gap_high = n2['High'], n['Low']
            filled, fill_time = check_fvg_filled(df, i, gap_low, gap_high, bullish=True)
            results.append({
                'Timestamp': ts,
                'Type': 'Bullish',
                'Gap_Low': gap_low,
                'Gap_High': gap_high,
                'Filled': filled,
                'Fill_Time': fill_time
            })
        # Bearish FVG
        if n2['Low'] > n['High']:
            gap_low, gap_high = n['High'], n2['Low']
            filled, fill_time = check_fvg_filled(df, i, gap_low, gap_high, bullish=False)
            results.append({
                'Timestamp': ts,
                'Type': 'Bearish',
                'Gap_Low': gap_low,
                'Gap_High': gap_high,
                'Filled': filled,
                'Fill_Time': fill_time
            })
    return pd.DataFrame(results)

def check_fvg_filled(df: pd.DataFrame, start_idx: int, gap_low: float, gap_high: float, bullish: bool) -> (bool, Optional[pd.Timestamp]):
    """
    Check if the FVG is filled after its creation.
    For bullish: any candle's low <= gap_low (gap filled from below)
    For bearish: any candle's high >= gap_high (gap filled from above)
    Returns (filled: bool, fill_time: pd.Timestamp or None)
    """
    for j in range(start_idx+1, len(df)):
        row = df.iloc[j]
        if bullish and row['Low'] <= gap_low:
            return True, df.index[j]
        if not bullish and row['High'] >= gap_high:
            return True, df.index[j]
    return False, None

def analyze_fvgs(fvg_df: pd.DataFrame) -> dict:
    """
    Generate summary insights from the FVG DataFrame.
    Returns a dictionary of stats.
    """
    if fvg_df.empty:
        return {'total_fvgs': 0}
    total = len(fvg_df)
    filled = fvg_df['Filled'].sum()
    fill_rate = filled / total if total > 0 else 0
    avg_gap = (fvg_df['Gap_High'] - fvg_df['Gap_Low']).mean()
    min_gap = (fvg_df['Gap_High'] - fvg_df['Gap_Low']).min()
    max_gap = (fvg_df['Gap_High'] - fvg_df['Gap_Low']).max()
    # By type
    bullish = fvg_df[fvg_df['Type'] == 'Bullish']
    bearish = fvg_df[fvg_df['Type'] == 'Bearish']
    bullish_count = len(bullish)
    bearish_count = len(bearish)
    bullish_filled = bullish['Filled'].sum() if not bullish.empty else 0
    bearish_filled = bearish['Filled'].sum() if not bearish.empty else 0
    # Gap stats by type
    bullish_gap = (bullish['Gap_High'] - bullish['Gap_Low']) if not bullish.empty else pd.Series(dtype=float)
    bearish_gap = (bearish['Gap_High'] - bearish['Gap_Low']) if not bearish.empty else pd.Series(dtype=float)
    # Avg time to fill (in periods)
    filled_fvgs = fvg_df[fvg_df['Filled']]
    if not filled_fvgs.empty:
        time_to_fill = (pd.to_datetime(filled_fvgs['Fill_Time']) - pd.to_datetime(filled_fvgs['Timestamp'])).dt.total_seconds() / 60
        avg_time_to_fill = time_to_fill.mean()
        min_time_to_fill = time_to_fill.min()
        max_time_to_fill = time_to_fill.max()
    else:
        avg_time_to_fill = min_time_to_fill = max_time_to_fill = None
    # Largest FVG
    fvg_df['Gap_Size'] = fvg_df['Gap_High'] - fvg_df['Gap_Low']
    largest_fvg = fvg_df.loc[fvg_df['Gap_Size'].idxmax()] if not fvg_df.empty else None
    # First/last FVG
    first_fvg = fvg_df.iloc[0]['Timestamp'] if not fvg_df.empty else None
    last_fvg = fvg_df.iloc[-1]['Timestamp'] if not fvg_df.empty else None
    return {
        'total_fvgs': total,
        'bullish_fvgs': bullish_count,
        'bearish_fvgs': bearish_count,
        'filled_fvgs': int(filled),
        'unfilled_fvgs': int(total - filled),
        'fill_rate': fill_rate,
        'bullish_filled': int(bullish_filled),
        'bearish_filled': int(bearish_filled),
        'bullish_fill_rate': bullish_filled / bullish_count if bullish_count else 0,
        'bearish_fill_rate': bearish_filled / bearish_count if bearish_count else 0,
        'avg_gap_size': avg_gap,
        'min_gap_size': min_gap,
        'max_gap_size': max_gap,
        'avg_bullish_gap': bullish_gap.mean() if not bullish_gap.empty else None,
        'avg_bearish_gap': bearish_gap.mean() if not bearish_gap.empty else None,
        'avg_time_to_fill_min': avg_time_to_fill,
        'min_time_to_fill_min': min_time_to_fill,
        'max_time_to_fill_min': max_time_to_fill,
        'largest_fvg': {
            'Timestamp': largest_fvg['Timestamp'],
            'Type': largest_fvg['Type'],
            'Gap_Size': largest_fvg['Gap_Size'],
            'Gap_Low': largest_fvg['Gap_Low'],
            'Gap_High': largest_fvg['Gap_High'],
        } if largest_fvg is not None else None,
        'first_fvg_timestamp': first_fvg,
        'last_fvg_timestamp': last_fvg,
    }

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    # Example: load a CSV and detect FVGs
    if len(sys.argv) > 1:
        df = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True)
        fvg_df = detect_fvg(df)
        print(fvg_df.head())
        print(analyze_fvgs(fvg_df)) 