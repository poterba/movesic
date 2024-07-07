# fmt: off
from multiprocessing import freeze_support
freeze_support()
# fmt: on


from nicegui import ui
import logging
from movesic.gui.widgets import *


def main():
    logging.basicConfig(level=logging.DEBUG)
    ui.run(
        native=True,
        reload=False,
        title="movesic",
        favicon="📻",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
