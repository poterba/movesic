# ruff: noqa: E402
# fmt: off
from multiprocessing import freeze_support
freeze_support()
# fmt: on

from logging.handlers import RotatingFileHandler
import sys
import threading
import logging
from nicegui import app, ui
from movesic import config, database
from movesic.database.migrations import run_migrations
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

def stretch_page():
    # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
    ui.query(".q-page").classes("flex")
    ui.query(".nicegui-content").classes("w-full")

app.on_startup(movesic_init)
app.on_connect(stretch_page)

@ui.page("/")
async def index_page():

    with ui.left_drawer(value=True) as drawer:
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
    logging_handlers = [
        logging.StreamHandler(sys.stdout),
    ]
    if config.MovesicConfig.NATIVE_APP:
        logging_handlers.append(
            RotatingFileHandler(
                "movesic.log",
                maxBytes=1024 * 1024,
                backupCount=3,
            )
        )
    logging.basicConfig(
        level=config.MovesicConfig.LOGGING_LEVEL,
        handlers=logging_handlers,
    )
    ui.run(
        native=config.MovesicConfig.NATIVE_APP,
        reload=False,
        show=False,
        dark=True,
        title=f"MoveSIC {config.MovesicConfig.VERSION}",
        favicon="📻",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
