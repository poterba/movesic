# fmt: off
from multiprocessing import freeze_support
import threading

from movesic.database.migrations import run_migrations
freeze_support()
# fmt: on

import logging
from nicegui import app, ui
from movesic import config, database
from movesic.gui import widgets


def movesic_init():
    migrate = threading.Thread(
        target=run_migrations,
        args=(config.MovesicConfig.DATABASE_URL,),
    )
    migrate.start()
    migrate.join()

    logging.info(f"Using storage: {config.MovesicConfig.STORAGE_PATH}")
    database.init(config.MovesicConfig.DATABASE_URL)


app.on_startup(movesic_init)


@ui.page("/")
async def index_page():
    with ui.left_drawer(value=False) as drawer:
        with ui.card().classes("w-full"):
            ui.label("Applications")
            await widgets.applications()
        with ui.card().classes("w-full"):
            ui.label("Credentials")
            await widgets.credentials()

    with ui.header():
        ui.button(icon="settings", on_click=lambda: drawer.toggle())

    await widgets.show_index()


def main():
    logging.basicConfig(level=logging.DEBUG)
    ui.run(
        native=True,
        reload=False,
        dark=True,
        title=f"MoveSIC {config.MovesicConfig.VERSION}",
        favicon="📻",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
