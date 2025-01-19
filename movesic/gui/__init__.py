from nicegui import ui, app

from movesic.engines import spotify, youtube
from movesic.gui import widgets


@ui.page("/")
def index():
    widgets.show_header()
    widgets.show_index()


@ui.page("/settings")
def youtube_page():
    widgets.show_header()
    if "youtube_app" in app.storage.general:
        values = app.storage.general["youtube_app"]
        yt = youtube.Youtube(
            auth=app.storage.general["youtube"], # "oauth.json",
            client_id=values["client_id"],
            secret=values["secret"],
        )
        widgets.show_engine(yt, "youtube")
    else:
        widgets.show_youtube_setup()

    if "spotify_app" in app.storage.general:
        config = app.storage.general["spotify_app"]
        sp = spotify.Spotify(
            config["client_id"],
            config["secret"],
            spotify.StorageCacheHandler(app.storage.general),
        )
        widgets.show_engine(sp, "spotify")
    else:
        widgets.show_spotify_setup()
