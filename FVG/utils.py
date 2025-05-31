import os
import logging

def ensure_output_dir(path: str):
    """
    Ensure the output directory exists.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def setup_logging():
    """
    Set up logging format and level.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ) 