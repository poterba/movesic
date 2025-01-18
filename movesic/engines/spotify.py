import spotipy
from spotipy import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

from movesic.engines import api

scope = "user-library-read"


class StorageCacheHandler(CacheHandler):
    def __init__(self, storage):
        super().__init__()
        self.storage = storage

    def get_cached_token(self):
        """
        Get and return a token_info dictionary object.
        """
        if "spotify" in self.storage:
            return self.storage["spotify"]
        return None

    def save_token_to_cache(self, token_info):
        """
        Save a token_info dictionary object to the cache and return None.
        """
        self.storage["spotify"] = token_info
        return None


class Spotify(api.Engine):
    def __init__(self, client_id, client_secret, cache_handler):
        # auth_manager = SpotifyClientCredentials(client_id, client_secret)
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:44444/",
            scope=scope,
            # open_browser=False,
            cache_handler=cache_handler,
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        # self.auth_manager = SpotifyOAuth(client_id, client_secret, scope=scope)

    def get_playlists(self):
        query_result = self.sp.current_user_playlists()
        result = []
        for item in query_result["items"]:
            result.append(
                api.Playlist(
                    name=item["name"],
                    id=item["id"],
                    external_url=item["external_urls"]["spotify"],
                )
            )
        return result

    def get_songs(self, playlist):
        query_result = self.sp.playlist(playlist.id)
        result = [self._to_song(x["track"]) for x in query_result["tracks"]["items"]]
        return result

    def find_song(self, name, author=None):
        query_result = self.sp.search(f"{author} {name}")
        result = [self._to_song(x) for x in query_result["tracks"]["items"]]
        return result

    def _to_song(self, track):
        authors = ", ".join([x["name"] for x in track["artists"]])
        return api.Song(
            name=track["name"],
            author=authors,
            id=track["id"],
            external_url=track["href"]
        )
