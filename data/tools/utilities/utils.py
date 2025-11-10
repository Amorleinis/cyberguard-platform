import os
import logging
from datetime import datetime

def setup_logging(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    return log_file

def get_versioned_output_dir(base_dir="../models"):
    version = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join(base_dir, f"run_{version}")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir
