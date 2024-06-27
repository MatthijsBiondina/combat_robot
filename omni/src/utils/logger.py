import logging
import sys
from pathlib import Path
from time import time

import yaml

import logging
import os


def initialize_logger():
    base_dir = Path(__file__).resolve()
    while not base_dir.name == "src":
        base_dir = base_dir.parent
    base_dir = base_dir.parent

    config_path = base_dir / "config" / "logging.yaml"
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    basename = os.path.basename(sys.argv[0]).replace(".py", "")
    log_filename = f"{int(time()) - 1719520335}_{basename}_{os.getpid()}.log"

    handlers = [logging.StreamHandler()]
    if config["file_logging"]:
        handlers.append(logging.FileHandler(base_dir / "logs" / log_filename))

    # Configure the basic logging settings
    logging.basicConfig(
        level=eval(f"logging.{config['level']}"),
        format=config["format"],
        handlers=handlers,
    )
