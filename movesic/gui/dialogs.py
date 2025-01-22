import json
from nicegui import ui


from movesic.database import model

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
