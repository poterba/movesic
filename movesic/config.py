import importlib.metadata
import os
from pathlib import Path
import sys


class MovesicConfig:
    VERSION = importlib.metadata.version("movesic")

    DATABASE_URL = os.getenv(
        "MOVESIC_DATABASE_URL",
        "sqlite+aiosqlite:///movesic.sqlite",
    )
    STORAGE_PATH = os.getenv("MOVESIC_STORAGE_PATH", ".movesic")
    LOGGING_LEVEL = os.getenv("MOVESIC_LOGGING_LEVEL", "INFO")

    @staticmethod
    def resource(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return Path(base_path) / f"resources/{relative_path}"
