import os
import json
import logging
from typing import Dict

def save_insights_to_file(insights: Dict, ticker: str, timeframe: str, output_dir: str):
    """
    Save the insights dictionary to a JSON file in the output directory.
    The file is named {ticker}_{timeframe}_insights.json.
    """
    filename = f"{ticker}_{timeframe}_insights.json"
    path = os.path.join(output_dir, filename)
    with open(path, 'w') as f:
        json.dump(insights, f, indent=4, default=str)
    logging.info(f"Saved insights to {path}") 