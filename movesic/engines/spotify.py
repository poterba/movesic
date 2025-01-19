import asyncio
from datetime import datetime
import spotipy
from spotipy import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

from movesic.database import crud, model
from movesic.engines import api

_SPOTIFY_SCOPES = [
    "user-library-read",
    "user-library-modify",
    "playlist-modify-private",
    "playlist-modify-public",
]


class DBCacheHandler(CacheHandler):
    def __init__(self, cred: model.Credentials):
        super().__init__()
        self.cred = cred

    async def save_token_to_cache(self, token_info):
        self.cred.data = token_info
        asyncio.run_coroutine_threadsafe(self.save_to_db(), None)

    def get_cached_token(self):
        if self.cred:
            return self.cred.data
        return None

    async def save_to_db(self):
        if self.cred:
            await crud.update_credentials(
                self.cred.id,
                data=self.cred.data,
            )
        else:
            self.cred = await crud.create_credentials(
                type=model.SERVICETYPE_ENUM.SPOTIFY,
                date_created=datetime.now(),
                data=self.cred.data,
            )


class Spotify(api.Engine):
    def __init__(self, creds: model.Credentials, app: model.Application):
        auth_manager = SpotifyOAuth(
            **app.data,
            redirect_uri="http://localhost:44444/",
            scope=",".join(_SPOTIFY_SCOPES),
            cache_handler=DBCacheHandler(creds),
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def info(self):
        info = self.sp.current_user()
        return api.UserInfo(
            name=info["display_name"],
            avatar=info["images"][0]["url"],
            id=info["id"],
            external_url=info["external_urls"]["spotify"],
        )

    # playlist

    def get_playlists(self):
        query_result = self.sp.current_user_playlists()
        result = [self._to_playlist(item) for item in query_result["items"]]
        return result

    def get_playlist(self, id):
        _result = self.sp.playlist(id)
        return self._to_playlist(_result)

    def add_playlist(self, name, description="") -> api.Playlist:
        _user = self.sp.current_user()
        _result = self.sp.user_playlist_create(
            _user["id"],
            name=name,
            public=False,
            description=description,
        )
        return self._to_playlist(_result)

    def delete_playlist(self, playlist: api.Playlist):
        return self.sp.current_user_unfollow_playlist(playlist.id)

    # songs

    def get_songs(self, playlist):
        query_result = self.sp.playlist(playlist.id)
        result = [self._to_song(x["track"]) for x in query_result["tracks"]["items"]]
        return result

    def find_song(self, name, author=None):
        query_result = self.sp.search(f"{author} {name}")
        result = [self._to_song(x) for x in query_result["tracks"]["items"]]
        return result

    # util

    def _to_song(self, track):
        authors = ", ".join([x["name"] for x in track["artists"]])
        return api.Song(
            name=track["name"],
            author=authors,
            id=track["id"],
            external_url=track["href"],
        )

    def _to_playlist(self, item):
        return api.Playlist(
            name=item["name"],
            id=item["id"],
            external_url=item["external_urls"]["spotify"],
        )
