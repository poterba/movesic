import webbrowser
from functools import partial

from nicegui import app, ui

from movesic.engines import api

_SPOTIFY_MD = """
You should create app and get some keys. Tick `Web API` checkbox.
| Option | Value |
| ------------- | ------------- |
| App name | *Anything* |
| App description | *Anything* |
| Redirect URIs | http://localhost:44444/ |
| Which API/SDKs are you planning to use? | Web API |
"""

_YOUTUBE_MD = ""


def _set_config(name, config):
    app.storage.general[name] = config
    ui.navigate.reload()


def _erase_config(name):
    del app.storage.general[name]
    ui.navigate.reload()


def show_header():
    tabs_dict = {
        "HOME": "/",
        "YOUTUBE": "/youtube",
        "SPOTIFY": "/spotify",
    }
    with ui.header():
        ui.space()
        with ui.button_group():
            for t in tabs_dict:
                ui.button(t, on_click=partial(ui.navigate.to, tabs_dict[t]))
        ui.space()


def show_index():
    available_services = []
    for service in ["youtube", "spotify"]:
        if service in app.storage.general:
            available_services.append(service)

    if len(available_services) < 2:
        ui.label("Register 2 or more services")
    else:
        with ui.row(wrap=False).classes("w-full"):
            ui.select(available_services).classes("w-full")
            ui.select(available_services).classes("w-full")
        ui.button("RUN").classes("w-full")


def show_youtube_setup():
    ui.markdown(_YOUTUBE_MD)
    ui.button(
        "To My dashboard",
        on_click=lambda: webbrowser.open("https://console.cloud.google.com/auth"),
    )
    values = {"client_id": "", "secret": ""}
    if "youtube_app" in app.storage.general:
        values = app.storage.general["youtube_app"]
    client_id = ui.input(placeholder="Client ID", value=values["client_id"]).classes(
        "w-full"
    )
    secret = ui.input(placeholder="Client secret", value=values["secret"]).classes(
        "w-full"
    )
    ui.button(
        "Save",
        on_click=lambda: _set_config(
            "youtube_app",
            {"client_id": client_id.value, "secret": secret.value},
        ),
    )


def show_spotify_setup():
    with ui.card().classes("w-full"):
        ui.markdown(_SPOTIFY_MD)
        ui.button(
            "To My dashboard",
            on_click=lambda: webbrowser.open(
                "https://developer.spotify.com/dashboard/applications"
            ),
        )
        client_id = ui.input(placeholder="Client ID").classes("w-full")
        secret = ui.input(placeholder="Client secret").classes("w-full")
        ui.button(
            "Save",
            on_click=lambda: _set_config(
                "spotify_app",
                {"client_id": client_id.value, "secret": secret.value},
            ),
        )


def show_engine(eng: api.Engine, config_key: str):
    def _open_playlist(p):
        webbrowser.open(p.external_url)

    with ui.card().classes("w-full"):
        ui.label("Your playlists:")
        with ui.list().classes("w-full"):
            p: api.Playlist
            for p in eng.get_playlists():
                with ui.item(on_click=partial(_open_playlist, p)):
                    with ui.item_section():
                        ui.item_label(p.name)
                        ui.item_label(p.id).props("caption")

        ui.button("Reset", on_click=lambda: _erase_config(config_key)).classes("w-full")
