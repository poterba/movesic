import deezer
from fastapi import Request
from fastapi.responses import RedirectResponse
from social_core.backends.deezer import DeezerOAuth2
from social_core.strategy import BaseStrategy
from movesic.database import model
from movesic.engines import api


SOCIAL_AUTH_SETTINGS = {
    "SOCIAL_AUTH_DEEZER_KEY": "YOUR_DEEZER_APP_ID",
    "SOCIAL_AUTH_DEEZER_SECRET": "YOUR_DEEZER_APP_SECRET",
    "SOCIAL_AUTH_DEEZER_SCOPE": ["basic_access", "email"],
    "SOCIAL_AUTH_LOGIN_REDIRECT_URL": "/profile",
    "SOCIAL_AUTH_LOGIN_ERROR_URL": "/error",
}


class DeezerStrategy(BaseStrategy):
    def __init__(self, request: Request):
        self.request = request

    def request_data(self, merge=True):
        return dict(self.request.query_params)

    def redirect(self, url):
        return RedirectResponse(url)

    def absolute_uri(self, path=None):
        base = str(self.request.base_url).rstrip("/")
        return base + (path or "")

    def get_setting(self, name):
        return SOCIAL_AUTH_SETTINGS.get(name)


class Deezer(api.Engine):
    def __init__(
        self,
        app: model.Application,
        creds: model.Credentials | None = None,
    ):
        self.app = app
        self.creds = creds
        self.client = deezer.Client(
            headers={"Accept-Encoding": "identity"},
        )

    # user

    def info(self) -> api.UserInfo | None:
        user = self.client.get_user()
        return api.UserInfo(
            name=user.name,
            avatar=user.picture,
            id=str(user.id),
            external_url=user.link,
        )

    def authenticate(self):
        oauth = DeezerOAuth2(strategy=DeezerStrategy())
        params = oauth.auth_complete_params()
        return params

    # playlists

    def get_playlists(self) -> list[api.Playlist]: ...

    def get_playlist(self, id) -> api.Playlist: ...

    def add_playlist(self, name, description="") -> api.Playlist: ...

    def delete_playlist(self, playlist: api.Playlist): ...

    # songs

    def get_songs(self, playlist: api.Playlist) -> list[api.Song]: ...

    def find_song(self, name, author=None) -> list[api.Song]: ...

    def add_song_to_playlist(self, song: api.Song, playlist: api.Playlist): ...
