import importlib.metadata
import os
import platformdirs
from pathlib import Path
import sys


class MovesicConfig:
    VERSION = importlib.metadata.version("movesic")

    STORAGE_PATH = os.getenv(
        "MOVESIC_STORAGE_PATH", platformdirs.user_data_dir("movesic")
    )
    os.makedirs(STORAGE_PATH, exist_ok=True)

    DATABASE_URL = os.getenv(
        "MOVESIC_DATABASE_URL",
        f"sqlite+aiosqlite:////{STORAGE_PATH}/movesic.sqlite",
    )
    LOGGING_LEVEL = os.getenv("MOVESIC_LOGGING_LEVEL", "INFO")
    try:
        import webview  # type: ignore

        NATIVE_APP = True
    except ModuleNotFoundError:
        NATIVE_APP = False

    @staticmethod
    def resource(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return Path(base_path) / f"resources/{relative_path}"

    @staticmethod
    def get_string(key):
        import lxml.etree as ET

        root = ET.parse(MovesicConfig.resource("strings.xml"))
        for element in root.iter("*"):
            if not hasattr(element, "tag"):
                continue
            if element.tag == "string" and element.attrib.get("id") == key:
                return element.text or ""
        return ""
