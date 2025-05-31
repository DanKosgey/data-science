import pandas as pd
import os
from visualize_fvg import plot_fvgs

def synthetic_ohlcv():
    data = [
        [10, 12, 9, 11, 1000],
        [11, 13, 10, 12, 1100],
        [12, 14, 11, 13, 1200],
        [13, 15, 12, 14, 1300],
    ]
    idx = pd.date_range('2023-01-01', periods=len(data), freq='1H')
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=idx)
    return df

def synthetic_fvg():
    return pd.DataFrame([
        {'Timestamp': '2023-01-03 00:00:00', 'Type': 'Bullish', 'Gap_Low': 12, 'Gap_High': 14, 'Filled': False, 'Fill_Time': None},
    ])

def test_plot_fvgs(tmp_path):
    df = synthetic_ohlcv()
    fvg_df = synthetic_fvg()
    output_path = tmp_path / "fvg_plot.png"
    plot_fvgs(df, fvg_df, '1h', str(output_path))
    assert os.path.exists(output_path) 