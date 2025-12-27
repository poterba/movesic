from datetime import datetime
import webbrowser
from functools import partial
import human_readable

from nicegui import ui

from movesic import config
from movesic.database import crud, model
from movesic.engines import api, spotify, youtube
from movesic.gui import dialogs

_APP_LOGOS = {
    model.SERVICETYPE_ENUM.SPOTIFY: "icon/spotify.png",
    model.SERVICETYPE_ENUM.YOUTUBE_MUSIC: "icon/ytmusic.png",
}


class EnginePreview(ui.card):
    def __init__(self, creds, is_dest: bool, *, align_items=None):
        super().__init__(align_items=align_items)
        self.is_dest = is_dest
        self.creds = None
        self.current_playlist = None
        self.engine: api.Engine | None = None
        with self:
            self._ui(creds)

    def _ui(self, creds):
        self.creds_select = (
            ui.select(
                creds,
                on_change=self._on_engine_change,
            )
            .classes("w-full")
            .bind_value(self, "creds")
        )
        self.show_engine_info()
        self.current_playlist_select = (
            ui.select({}, on_change=self._on_playlist_change)
            .classes("w-full")
            .bind_value(self, "current_playlist")
            .bind_visibility_from(self, "engine")
        )
        self.show_playlist()

    async def _on_engine_change(self, event):
        try:
            creds: model.Credentials = event.value
            if not creds:
                return
            app = await crud.get_application(creds.app_id)
            if not app:
                raise RuntimeError("Not found apps for these creds")

            self.engine = self._to_engine(app, creds)

            playlists = self.engine.get_playlists()
            playlists = {x: x.name for x in playlists}
            if self.is_dest:
                playlists[None] = "Create new playlist"
            self.current_playlist_select.set_options(playlists)
        except Exception as e:
            ui.notify(f"Failed to load engine: {e}", type="negative")
            event.sender.set_value(None)
            self.engine = None
            self.current_playlist = None
        finally:
            self.show_engine_info.refresh()
            self.show_playlist.refresh()

    def _to_engine(self, app, creds):
        if app.type == model.SERVICETYPE_ENUM.YOUTUBE_MUSIC:
            return youtube.Youtube(app, creds)
        elif app.type == model.SERVICETYPE_ENUM.SPOTIFY:
            return spotify.Spotify(app, creds)
        else:
            raise RuntimeError(f"Unknown service {creds.type}")

    async def _on_playlist_change(self, event):
        self.show_playlist.refresh()

    @ui.refreshable
    def show_engine_info(self):
        if not self.engine:
            ui.label("Select some credentials")
            return
        user_info = self.engine.info()
        with ui.item().classes("w-full") as user_item:
            if user_info.avatar:
                with ui.item_section().props("avatar"):
                    ui.image(user_info.avatar)
            with ui.item_section():
                ui.item_label(user_info.name)
                ui.item_label(user_info.id).props("caption")
        if user_info.external_url:
            user_item.on_click(partial(webbrowser.open, user_info.external_url))

    @ui.refreshable
    def show_playlist(self):
        if not self.current_playlist:
            ui.label("Select some playlist")
            return

        songs = self.engine.get_songs(self.current_playlist)
        ui.label(f"{len(songs)} songs")
        with ui.scroll_area().classes("flex-grow"), ui.list().classes("w-full"):
            song: api.Song
            for song in songs:
                with ui.item().classes("w-full") as playlist_item:
                    if song.cover:
                        with ui.item_section().props("avatar"):
                            ui.image(song.cover)
                    with ui.item_section():
                        ui.item_label(song.name)
                        ui.item_label(song.album).props("caption")
                    with ui.item_section():
                        ui.item_label(song.author)
                if song.external_url:
                    playlist_item.on_click(
                        partial(webbrowser.open, song.external_url),
                    )


async def show_index():
    _creds = await crud.get_credentials()
    _apps = {}
    creds_to_apps = {}
    for cred in _creds:
        if cred.app_id not in _apps:
            _apps[cred.app_id] = await crud.get_application(cred.app_id)
        app = _apps[cred.app_id]
        creds_to_apps[cred] = f"{app.type.name} {cred.date_created}"

    with ui.splitter(limits=(50, 50)).classes("w-full flex-grow") as _splitter:
        with _splitter.before:
            left_engine = EnginePreview(creds_to_apps, False).classes(
                "w-full flex-grow"
            )
        with _splitter.after:
            right_engine = EnginePreview(creds_to_apps, True).classes(
                "w-full flex-grow"
            )

    async def _start_move():
        result = await dialogs.MoveDialog(
            left_engine.engine,
            left_engine.current_playlist,
            right_engine.engine,
            right_engine.current_playlist,
        )
        if result:
            ui.notify("Successfully moved!")

    ui.button("RUN", on_click=_start_move).classes("w-full").bind_enabled_from(
        locals(),
        "left_engine",
        lambda x: x.current_playlist
        and right_engine.creds
        and (right_engine.creds != left_engine.creds or not right_engine.current_playlist),
    )
    with ui.row(wrap=False).classes("w-full"):
        ui.list()


async def _edit_app(application=None, *args, **kwargs):
    result = await dialogs.EditApplicationDialog(application)
    if result:
        if result.id:
            # TODO
            pass
        else:
            result.date_created = datetime.now()
            await crud.create_application(result)
        ui.navigate.reload()


async def _edit_cred(credentials, *args, **kwargs):
    apps = await crud.get_application()
    result: model.Credentials | None = await dialogs.EditCredentialsDialog(credentials, apps)
    if result:
        if result.id:
            await crud.update_credentials(
                result.id,
                app_id=result.app_id,
                username=result.username,
                data=result.data,
            )
        else:
            await crud.create_credentials(result)
        ui.navigate.reload()


async def applications():
    apps = await crud.get_application()
    with ui.list().classes("w-full"):
        app: model.Application
        for app in apps:
            with ui.item(on_click=partial(_edit_app, app)).classes("w-full"):
                with ui.item_section().props("avatar"):
                    ui.image(config.MovesicConfig.resource(_APP_LOGOS[app.type]))
                with ui.item_section():
                    ui.item_label(app.name)
                    when = human_readable.date_time(app.date_created)
                    ui.item_label(when).props("caption")
        ui.button(icon="add", on_click=_edit_app).classes("w-full")


async def credentials():
    creds = await crud.get_credentials()
    with ui.list().classes("w-full"):
        cred: model.Credentials
        for cred in creds:
            app = await crud.get_application(cred.app_id)
            with ui.item(on_click=partial(_edit_cred, cred)).classes("w-full"):
                with ui.item_section().props("avatar"):
                    ui.image(config.MovesicConfig.resource(_APP_LOGOS[app.type]))
                with ui.item_section():
                    ui.item_label(cred.username)
                    when = human_readable.date_time(cred.date_created)
                    ui.item_label(when).props("caption")
