import argparse
import os
import pandas as pd
from download_data import download_data
from resample_data import resample_data, SUPPORTED_TIMEFRAMES
from detect_fvg import detect_fvg, analyze_fvgs
from visualize_fvg import plot_fvgs, plot_fvg_duration_histogram, plot_fvg_frequency_timeseries
from utils import ensure_output_dir, setup_logging
from results import save_insights_to_file

def save_fvgs_to_csv(fvg_df: pd.DataFrame, ticker: str, timeframe: str, output_dir: str):
    """
    Save FVG DataFrame to CSV in the output directory.
    """
    filename = f"{ticker}_{timeframe}_fvgs.csv"
    path = os.path.join(output_dir, filename)
    fvg_df.to_csv(path, index=False)
    print(f"Saved FVGs to {path}")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Detect and visualize Fair Value Gaps (FVGs) across timeframes.")
    parser.add_argument('--ticker', required=True, help='Stock ticker symbol')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--timeframes', nargs='+', required=True, help='List of timeframes (e.g. 1D 12h 1h 15min)')
    args = parser.parse_args()

    output_dir = 'fvgs_output'
    ensure_output_dir(output_dir)

    df = download_data(args.ticker, args.start, args.end)
    if df.empty:
        print("No data downloaded. Exiting.")
        return
    df.index = pd.to_datetime(df.index)

    for tf in args.timeframes:
        if tf not in SUPPORTED_TIMEFRAMES:
            print(f"Skipping unsupported timeframe: {tf}")
            continue
        resampled = resample_data(df, tf)
        if resampled.empty:
            print(f"No data after resampling to {tf}. Skipping.")
            continue
        fvg_df = detect_fvg(resampled)
        save_fvgs_to_csv(fvg_df, args.ticker, tf, output_dir)
        plot_path = os.path.join(output_dir, f"{args.ticker}_{tf}_fvg_plot.png")
        plot_fvgs(resampled, fvg_df, tf, plot_path)
        # New: plot FVG duration histogram
        duration_hist_path = os.path.join(output_dir, f"{args.ticker}_{tf}_fvg_duration_hist.png")
        plot_fvg_duration_histogram(fvg_df, duration_hist_path)
        # New: plot FVG frequency timeseries
        freq_timeseries_path = os.path.join(output_dir, f"{args.ticker}_{tf}_fvg_frequency_timeseries.png")
        plot_fvg_frequency_timeseries(fvg_df, freq_timeseries_path)
        insights = analyze_fvgs(fvg_df)
        print(f"Insights for {tf}: {insights}")
        save_insights_to_file(insights, args.ticker, tf, output_dir)

if __name__ == "__main__":
    main() 