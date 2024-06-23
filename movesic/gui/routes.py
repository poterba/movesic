from nicegui import ui
from ytmusicapi import YTMusic


@ui.page("/")
def index():
    ytmusic = YTMusic()
    home = ytmusic.get_home()
    with ui.list().classes("w-full"):
        for playlist in home:
            with ui.item(on_click=lambda: ui.notify("login please")):
                with ui.item_section():
                    ui.item_label(playlist["title"])
                    # ui.item_label(playlist["title"])
