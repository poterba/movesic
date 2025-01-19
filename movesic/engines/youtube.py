import logging
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
        self.ytmusic = YTMusic(
            auth=auth,
            oauth_credentials=oauth_credentials,
        )

    def info(self):
        info = self.ytmusic.get_account_info()
        return api.UserInfo(
            name=info["accountName"],
            avatar=info["accountPhotoUrl"],
            id=info["channelHandle"],
            # TODO
            external_url=None,
        )

    # playlists

    def get_playlists(self):
        playlists = self.ytmusic.get_library_playlists(limit=None)
        playlists = [self._to_playlist(x) for x in playlists]
        return playlists

    def get_playlist(self, id):
        _result = self.ytmusic.get_playlist(id, limit=0)
        return self._to_playlist(_result)

    def add_playlist(self, name, description=""):
        playlistId = self.ytmusic.create_playlist(name, description)
        return self.get_playlist(playlistId)

    def delete_playlist(self, playlist):
        _result = self.ytmusic.delete_playlist(playlist.id)
        logging.info(_result)
        return _result

    # songs

    def get_songs(self, playlist: api.Playlist):
        results = self.ytmusic.get_playlist(playlist.id, limit=None)
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

    def add_song_to_playlist(self, song: api.Song, playlist: api.Playlist):
        self.ytmusic.add_playlist_items(playlist.id, [song.id])

    # util

    def _to_song(self, x):
        author_str = ", ".join([a["name"] for a in x["artists"]])
        return api.Song(
            name=x["title"],
            author=author_str,
            id=x["videoId"],
            external_url=f"https://music.youtube.com/watch?v={x['videoId']}",
        )

    def _to_playlist(self, x):
        _id = None
        for tag in ["id", "playlistId"]:
            if tag in x:
                _id = x[tag]
                break
        assert _id
        return api.Playlist(
            name=x["title"],
            id=_id,
            external_url=f"https://music.youtube.com/playlist?list={_id}",
        )
