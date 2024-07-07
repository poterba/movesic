from nicegui import ui
from movesic.gui import widgets


@ui.page("/")
def index():
    widgets.header()
    widgets.index()


@ui.page("/youtube")
def youtube_page():
    widgets.header()
    widgets.youtube()


@ui.page("/spotify")
def spotify_page():
    widgets.header()
    widgets.spotify()
