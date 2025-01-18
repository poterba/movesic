from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials

from movesic.engines import api
from movesic.engines.api import Engine


class Youtube(Engine):
    def __init__(
        self,
        auth=None,
        *,
        client_id: str | None = None,
        secret: str | None = None,
    ):
        oauth_credentials = None
        if client_id and secret:
            oauth_credentials = OAuthCredentials(
                client_id=client_id,
                client_secret=secret,
            )
        self.ytmusic = YTMusic(auth=auth, oauth_credentials=oauth_credentials)

    def get_playlists(self):
        playlists = self.ytmusic.get_library_playlists(limit=None)
        playlists = [
            api.Playlist(
                name=x["title"],
                id=x["playlistId"],
                external_url=f"https://music.youtube.com/playlist?list={x['playlistId']}",
            )
            for x in playlists
        ]
        return playlists

    def get_songs(self, playlist: api.Playlist):
        results = self.ytmusic.get_playlist(
            playlist.id,
            limit=None,
        )
        results = [self._to_song(x) for x in results["tracks"]]
        return results

    def find_song(self, name, author=None):

        results = self.ytmusic.search(
            f"{author} - {name}",
            filter="songs",
            ignore_spelling=True,
            limit=3,
        )
        results = [self._to_song(x) for x in results]
        return results

    def _to_song(self, x):
        author_str = ", ".join([a["name"] for a in x["artists"]])
        return api.Song(
            name=x["title"],
            author=author_str,
            id=x["videoId"],
            external_url=f"https://music.youtube.com/watch?v={x['videoId']}",
        )