import asyncio
import logging
from datetime import datetime
import time
import webbrowser
from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken

from movesic.database import crud, model
from movesic.engines import api
from movesic.engines.api import Engine


class UserlessToken:
    def __init__(self, credentials: OAuthCredentials, app_id):
        self.credentials = credentials
        self.app_id = app_id

    def wait_for_token(self) -> RefreshingToken:
        code = self.credentials.get_code()
        url = f"{code['verification_url']}?user_code={code['user_code']}"
        webbrowser.open(url)

        while True:
            try:
                result = self.credentials.token_from_code(code["device_code"])
                if "error" in result:
                    logging.error(result["error"])
                    raise YTMusicUserError(
                        f"Authentication not finished yet: {result['error']}"
                    )
                logging.info("Youtube token obtained")
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(self.save_to_db(result), loop)
                return result
            except YTMusicUserError:
                time.sleep(5)

    async def save_to_db(self, creds):
        logging.info("Saving Youtube OAuth credentials to database")
        
        try:
            creds_obj = model.Credentials(
                app_id=self.app_id,
                date_created=datetime.now(),
                data=creds,
                username="Youtube Music Userless",
                avatar=None,
            )
            await crud.create_credentials(creds_obj)
        except Exception as e:
            logging.error(f"Failed to save Youtube OAuth credentials to database: {e}")


class Youtube(Engine):
    def __init__(
        self,
        app: model.Application,
        creds: model.Credentials | None = None,
    ):
        self.app = app
        self.creds = OAuthCredentials(**app.data)
        self.ytmusic = YTMusic(
            auth=creds.data if creds else None,
            oauth_credentials=self.creds,
        )

    def info(self):
        info = self.ytmusic.get_account_info()
        return api.UserInfo(
            name=info["accountName"],
            avatar=info["accountPhotoUrl"],
            id=info["channelHandle"],
            external_url=f"https://www.youtube.com/{info['channelHandle']}",
        )

    def authenticate(self):
        return UserlessToken(self.creds, self.app.id).wait_for_token()

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
        album_str = None
        if "album" in x and x["album"]:
            album_str = x["album"]["name"]

        return api.Song(
            id=x["videoId"],
            external_url=f"https://music.youtube.com/watch?v={x['videoId']}",
            name=x["title"],
            author=author_str,
            album=album_str,
            cover=x["thumbnails"][-1]["url"],
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
