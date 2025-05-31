import pandas as pd
import matplotlib.pyplot as plt
import logging

def plot_fvgs(df: pd.DataFrame, fvg_df: pd.DataFrame, timeframe: str, output_path: str):
    """
    Plot price data and overlay FVGs (bullish/bearish, filled/unfilled).
    Save the plot as a PNG to output_path.
    """
    plt.figure(figsize=(16, 8))
    plt.plot(df.index, df['Close'], label='Close', color='black', linewidth=1)
    # Plot FVGs
    for _, row in fvg_df.iterrows():
        color = 'green' if row['Type'] == 'Bullish' else 'red'
        alpha = 0.3 if not row['Filled'] else 0.1
        plt.axhspan(row['Gap_Low'], row['Gap_High'], xmin=0, xmax=1, color=color, alpha=alpha)
    plt.title(f'FVGs on {timeframe} Chart')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logging.info(f"Saved FVG plot to {output_path}")

def plot_fvg_duration_histogram(fvg_df: pd.DataFrame, output_path: str):
    """
    Plot a histogram of FVG fill durations (in minutes) for filled FVGs.
    """
    if fvg_df.empty or 'Filled' not in fvg_df.columns:
        logging.warning("No FVGs to plot duration histogram.")
        return
    filled = fvg_df[fvg_df['Filled']]
    if filled.empty:
        logging.warning("No filled FVGs to plot duration histogram.")
        return
    durations = (
        pd.to_datetime(filled['Fill_Time']) - pd.to_datetime(filled['Timestamp'])
    ).dt.total_seconds() / 60
    plt.figure(figsize=(10, 6))
    plt.hist(durations.dropna(), bins=30, color='blue', alpha=0.7)
    plt.title('Histogram of FVG Fill Durations (minutes)')
    plt.xlabel('Minutes to Fill')
    plt.ylabel('Number of FVGs')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logging.info(f"Saved FVG duration histogram to {output_path}")

def plot_fvg_frequency_timeseries(fvg_df: pd.DataFrame, output_path: str, freq: str = 'W'):
    """
    Plot a time series (bar chart) of FVG frequency per period (default: week).
    """
    if fvg_df.empty or 'Timestamp' not in fvg_df.columns:
        logging.warning("No FVGs to plot frequency timeseries.")
        return
    fvg_df['Timestamp'] = pd.to_datetime(fvg_df['Timestamp'])
    freq_series = fvg_df.groupby(pd.Grouper(key='Timestamp', freq=freq)).size()
    plt.figure(figsize=(12, 6))
    freq_series.plot(kind='bar', color='purple', alpha=0.7)
    plt.title(f'FVG Frequency per {freq}')
    plt.xlabel('Period')
    plt.ylabel('Number of FVGs')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logging.info(f"Saved FVG frequency timeseries to {output_path}")

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 2:
        df = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True)
        fvg_df = pd.read_csv(sys.argv[2])
        plot_fvgs(df, fvg_df, '1h', 'fvg_plot.png')
        plot_fvg_duration_histogram(fvg_df, 'fvg_duration_hist.png')
        plot_fvg_frequency_timeseries(fvg_df, 'fvg_frequency_timeseries.png') 