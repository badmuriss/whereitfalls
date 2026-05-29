import logging
import sys

from pythonjsonlogger import json


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = json.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
