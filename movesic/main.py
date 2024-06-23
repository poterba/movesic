from nicegui import ui
import logging
from movesic.gui.routes import *

if __name__ in {"__main__", "__mp_main__"}:
    logging.basicConfig(level=logging.DEBUG)
    ui.run(
        native=True,
        # reload=False,
        title="movesic",
        favicon="📻",
        # storage_secret=os.environ["STORAGE_SECRET"],
    )
