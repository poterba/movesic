import webbrowser
from functools import partial

from nicegui import app, ui

from movesic import engines

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


def header():
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


def index():
    available_services = []
    for service in ["youtube", "spotify"]:
        if service in app.storage.general:
            available_services.append(service)

    if len(available_services) < 2:
        ui.label("Register 2 or more services")
    else:
        with ui.row(wrap=False).classes("w-full"):
            ui.select(
                available_services, value=available_services[0]
            ).classes("w-full")
            ui.select(
                available_services, value=available_services[0]
            ).classes("w-full")
        ui.button("RUN").classes("w-full")


def youtube():
    with ui.card().classes("w-full"):
        if "youtube" in app.storage.general:
            yt = engines.Youtube()
            ui.label("Your playlists:")
            with ui.list().classes("w-full"):
                for p in yt.get_playlists():  # type: movesic.api.Playlist
                    ui.item(p.name, on_click=lambda: webbrowser.open(p.external_url))
        else:
            ui.markdown(_YOUTUBE_MD)
            # ui.button(
            #     "To My dashboard",
            #     on_click=lambda: webbrowser.open(
            #         "https://developer.spotify.com/dashboard/applications"
            #     ),
            # )
            client_id = ui.input(placeholder="Client ID").classes("w-full")
            secret = ui.input(placeholder="Client secret").classes("w-full")
            ui.button(
                "Save",
                on_click=lambda: _set_config(
                    "spotify",
                    {"client_id": client_id.value, "secret": secret.value},
                ),
            )


def spotify():
    with ui.card().classes("w-full"):
        if "spotify" in app.storage.general:
            config = app.storage.general["spotify"]
            sp = engines.Spotify(config["client_id"], config["secret"])
            ui.label("Your playlists:")
            with ui.list().classes("w-full"):
                for p in sp.get_playlists():  # type: movesic.api.Playlist
                    ui.item(p.name, on_click=lambda: webbrowser.open(p.external_url))

            ui.button("Reset", on_click=lambda: _erase_config("spotify")).classes(
                "w-full"
            )
        else:
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
                    "spotify",
                    {"client_id": client_id.value, "secret": secret.value},
                ),
            )
