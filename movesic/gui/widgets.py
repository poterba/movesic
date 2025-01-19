from datetime import datetime
import webbrowser
from functools import partial

from nicegui import ui, run

from movesic import config
from movesic.database import crud, model
from movesic.engines import api, spotify, youtube
from movesic.gui import dialogs

_APP_LOGOS = {
    model.SERVICETYPE_ENUM.SPOTIFY: "icon/spotify.png",
    model.SERVICETYPE_ENUM.YOUTUBE_MUSIC: "icon/ytmusic.png",
}


@ui.refreshable
def show_engine(engine: api.Engine | None = None):
    def _open_playlist(p):
        webbrowser.open(p.external_url)

    with ui.card().classes("w-full"):
        if not engine:
            ui.label("Select saved credentials")
            return
        with ui.list().classes("w-full"):
            user_info = engine.info()
            with ui.item():
                if user_info.avatar:
                    with ui.item_section().props("avatar"):
                        ui.image(user_info.avatar)
                with ui.item_section():
                    ui.item_label(user_info.name)
                    ui.item_label(user_info.id).props("caption")
                if user_info.external_url:
                    with ui.item_section().props("side"):
                        ui.button(
                            icon="link",
                            on_click=partial(webbrowser.open, user_info.external_url),
                        ).props("outline")
            p: api.Playlist
            for p in engine.get_playlists():
                with ui.item(on_click=partial(_open_playlist, p)):
                    with ui.item_section():
                        ui.item_label(p.name)
                        ui.item_label(p.id).props("caption")



async def show_index():
    _creds = await crud.get_credentials()
    apps = await crud.get_application()
    creds = {}
    for cred in _creds:
        app = await crud.get_application(cred.app_id)
        creds[cred] = app.type.name
    items = {"left": None, "right": None}

    def _to_engine(app, creds):
        if app.type == model.SERVICETYPE_ENUM.YOUTUBE_MUSIC:
            return youtube.Youtube(creds, app)
        elif app.type == model.SERVICETYPE_ENUM.SPOTIFY:
            return spotify.Spotify(creds, app)
        else:
            raise RuntimeError(f"Unknown service {creds.type}")

    async def _refresh_engine(func, event):
        creds: model.Credentials = event.value
        app = await crud.get_application(creds.app_id)
        if not app:
            raise RuntimeError("Not found apps for these creds")
        await run.io_bound(func.refresh, _to_engine(app, creds))

    with ui.splitter(limits=(50, 50)).classes("w-full") as _splitter:
        with _splitter.before:
            left_sel = ui.select(creds).classes("w-full").bind_value(items, "left")
            left_engine = show_engine
            left_engine()
            left_sel.on_value_change(partial(_refresh_engine, left_engine))
        with _splitter.after:
            right_sel = ui.select(creds).classes("w-full").bind_value(items, "right")
            right_engine = show_engine
            right_engine()
            right_sel.on_value_change(partial(_refresh_engine, right_engine))
    ui.button("RUN").classes("w-full").bind_enabled_from(
        locals(),
        "items",
        lambda x: None not in x.values(),
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


async def _edit_cred(credentials=None, *args, **kwargs):
    apps = await crud.get_application()
    result = await dialogs.EditCredentialsDialog(credentials, apps)
    if result:
        if result.id:
            # TODO
            pass
        else:
            result.date_created = datetime.now()
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
                    ui.item_label(app.date_created)
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
                    ui.item_label(cred.date_created)
        ui.button(icon="add", on_click=_edit_cred).classes("w-full")
