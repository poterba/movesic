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

    def save_token_to_cache(self, token_info):
        self.cred.data = token_info
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(self.save_to_db(), loop)

    def get_cached_token(self):
        if self.cred:
            return self.cred.data
        return None

    async def save_to_db(self):
        if self.cred.id:
            await crud.update_credentials(
                self.cred.id,
                data=self.cred.data,
            )
        else:
            self.cred.date_created = datetime.now()
            await crud.create_credentials(self.cred)


class Spotify(api.Engine):
    def __init__(
        self,
        app: model.Application,
        creds: model.Credentials | None = None,
    ):
        self.app = app
        cache_handler = DBCacheHandler(
            creds
            or model.Credentials(
                app_id=app.id,
            )
        )
        auth_manager = SpotifyOAuth(
            **app.data,
            redirect_uri="http://127.0.0.1:44444/",
            scope=",".join(_SPOTIFY_SCOPES),
            cache_handler=cache_handler,
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

    def authenticate(self):
        info = self.sp.current_user()
        return info

        # auth_manager = SpotifyOAuth(
        #     redirect_uri="http://localhost:44444/",
        #     scope=",".join(_SPOTIFY_SCOPES),
        #     cache_handler=DBCacheHandler(creds) if creds else None,
        # )

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
            public=True,
            description=description,
        )
        result = self._to_playlist(_result)
        self.sp.current_user_follow_playlist(result.id)
        return result

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

    def add_song_to_playlist(self, song: api.Song, playlist: api.Playlist):
        result = self.sp.playlist_add_items(playlist.id, [song.id])
        return result

    # util

    def _to_song(self, track):
        authors = ", ".join([x["name"] for x in track["artists"]])
        return api.Song(
            id=track["id"],
            external_url=track["external_urls"]["spotify"],
            name=track["name"],
            author=authors,
            album=track["album"]["name"],
            cover=track["album"]["images"][0]["url"],
        )

    def _to_playlist(self, item):
        return api.Playlist(
            name=item["name"],
            id=item["id"],
            external_url=item["external_urls"]["spotify"],
        )
