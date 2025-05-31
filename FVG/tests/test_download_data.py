import pytest
from download_data import download_data

def test_download_data_valid(monkeypatch):
    # Monkeypatch yfinance to return a small DataFrame
    import pandas as pd
    class DummyTicker:
        @staticmethod
        def download(*args, **kwargs):
            idx = pd.date_range('2023-01-01', periods=2, freq='1T')
            return pd.DataFrame({
                'Open': [1, 2], 'High': [2, 3], 'Low': [0, 1], 'Close': [1.5, 2.5], 'Volume': [100, 200]
            }, index=idx)
    monkeypatch.setattr('yfinance.download', DummyTicker.download)
    df = download_data('AAPL', '2023-01-01', '2023-01-02')
    assert not df.empty
    assert set(['Open', 'High', 'Low', 'Close', 'Volume']).issubset(df.columns)

def test_download_data_invalid(monkeypatch):
    # Monkeypatch yfinance to return empty DataFrame
    import pandas as pd
    class DummyTicker:
        @staticmethod
        def download(*args, **kwargs):
            return pd.DataFrame()
    monkeypatch.setattr('yfinance.download', DummyTicker.download)
    df = download_data('INVALID', '2023-01-01', '2023-01-02')
    assert df.empty 