# fmt: off
from multiprocessing import freeze_support
freeze_support()
# fmt: on

import logging
from nicegui import ui
from movesic.gui.widgets import *  # noqa: F403


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
