import os
import logging
from utils import ensure_output_dir, setup_logging

def test_ensure_output_dir(tmp_path):
    test_dir = tmp_path / "test_output"
    ensure_output_dir(str(test_dir))
    assert os.path.exists(test_dir)

def test_setup_logging():
    setup_logging()
    logger = logging.getLogger()
    assert logger.level == logging.INFO or logger.level == 20  # INFO level 