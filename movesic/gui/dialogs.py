import asyncio
from functools import partial
import json
import logging
from typing import Optional
import webbrowser
from nicegui import run, ui


from movesic.database import model
from movesic.engines import api

_SPOTIFY_APP_MD = """
You should create app and get some keys. Tick `Web API` checkbox.
| Option | Value |
| ------------- | ------------- |
| App name | *Anything* |
| App description | *Anything* |
| Redirect URIs | http://localhost:44444/ |
| Which API/SDKs are you planning to use? | Web API |
"""

_YOUTUBE_APP_MD = """
You should create project on Dashboard. After add OAuth key on Auth page.
Add yourself on Audience page to test users.
"""

_PLAYLIST_DESCRIPTION = "Imported with MoveSIC"


class EditApplicationDialog(ui.dialog):
    def __init__(
        self,
        app: model.Application | None = None,
        *,
        value=False,
    ):
        super().__init__(value=value)
        if not app:
            app = model.Application(data={"client_id": "", "client_secret": ""})
        self.app = app
        with self, ui.card(align_items="stretch").classes("w-full"):
            self._ui()

    def _ui(self):
        types = {}
        for e in model.SERVICETYPE_ENUM:
            types[e] = e.name
        _props = "readonly" if self.app.id else ""
        _help_messages = {
            model.SERVICETYPE_ENUM.YOUTUBE_MUSIC: _YOUTUBE_APP_MD,
            model.SERVICETYPE_ENUM.SPOTIFY: _SPOTIFY_APP_MD,
            None: "",
        }
        "https://console.cloud.google.com/auth"
        "https://console.cloud.google.com/apis/credentials"
        "https://developer.spotify.com/dashboard/applications"

        type_select = (
            ui.select(
                types,
                value=self.app.type,
            )
            .bind_value(
                self.app,
                "type",
            )
            .props(_props)
        )
        if not self.app.id:
            ui.markdown().bind_content_from(
                type_select, "value", backward=lambda x: _help_messages[x]
            )
        ui.input(label="CLIENT_ID", value=self.app.data["client_id"]).bind_value(
            self.app.data, "client_id"
        ).props(_props)
        ui.input(label="SECRET", value=self.app.data["client_secret"]).bind_value(
            self.app.data, "client_secret"
        ).props(_props)
        if self.app.date_created:
            ui.label(self.app.date_created)
        if not self.app.id:
            ui.button(icon="save", on_click=lambda: self.submit(self.app))


class EditCredentialsDialog(ui.dialog):
    def __init__(
        self,
        creds: model.Credentials | None = None,
        apps: list[model.Application] = [],
        *,
        value=False,
    ):
        super().__init__(value=value)
        if not creds:
            creds = model.Credentials(data={})
        self.creds = creds
        self.apps = apps
        with self, ui.card(align_items="stretch").classes("w-full"):
            self._ui()

    def _ui(self):
        types = {}
        for e in model.SERVICETYPE_ENUM:
            types[e] = e.name
        _props = "readonly" if self.creds.id else ""
        apps = {}
        for a in self.apps:
            apps[a.id] = a.type.name
        ui.select(apps).bind_value(self.creds, "app_id").props(_props)
        self.editor = ui.json_editor(
            {
                "content": {"json": self.creds.data},
                "readOnly": bool(self.creds.id),
            },
            on_change=self._on_edit,
        )
        if not self.creds.id:
            ui.button(icon="save", on_click=lambda: self.submit(self.creds))

    def _on_edit(self, x):
        if x.errors:
            self.creds.data = {}
        else:
            if "text" in x.content:
                self.creds.data = json.loads(x.content["text"])
            elif "json" in x.content:
                self.creds.data = x.content["json"]


class MoveDialog(ui.dialog):
    def __init__(
        self,
        src: api.Engine,
        src_pl: api.Playlist,
        dest: api.Engine,
        dest_pl: api.Playlist,
        *,
        value=False,
    ):
        super().__init__(value=value)
        self.src = src
        self.src_pl = src_pl
        self.dest = dest
        self.dest_pl = dest_pl
        with self, ui.card().classes("w-full"):
            self._ui()

    def _ui(self):
        def _playlist(pl: api.Playlist | None):
            if not pl:
                return

            with ui.item().classes("w-full") as playlist_item:
                with ui.item_section():
                    ui.item_label(pl.name)
            if pl.external_url:
                playlist_item.on_click(partial(webbrowser.open, pl.external_url))

        with ui.row(wrap=False).classes("w-full"):
            _playlist(self.src_pl)
            _playlist(self.dest_pl)
        self.progress_bar = ui.linear_progress(show_value=False)
        self._left_song()
        # TODO: right

    def open(self):
        super().open()
        loop = asyncio.get_running_loop()
        self.future = loop.create_task(run.io_bound(self._move))
        asyncio.ensure_future(self.future)

    def close(self):
        super().close()
        self.future.cancel()
        self.submit(False)

    @ui.refreshable_method
    def _left_song(self, song: Optional[api.Song] = None):
        if not song:
            return
        self.left_song = ui.card(align_items="stretch")
        with self.left_song:
            if song.cover:
                ui.image(song.cover)
            ui.label(song.name)
            ui.label(f"{song.author} - {song.album}")

    def _move(self):
        if not self.dest_pl:
            self.dest_pl = self.dest.add_playlist(self.src_pl.name, _PLAYLIST_DESCRIPTION)
            logging.info(f"added playlist {self.dest_pl.name} {self.dest_pl.id}")

        songs = self.src.get_songs(self.src_pl)
        for index, s in enumerate(songs):
            self._left_song.refresh(s)
            result = self.dest.find_song(s.name, s.author)
            result = result[0]
            self.dest.add_song_to_playlist(song=result, playlist=self.dest_pl)
            logging.info(f"added song {result.author} - {result.name}")
            self.progress_bar.value = index / len(songs)
        self.submit(True)
