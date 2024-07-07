import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials, SpotifyPKCE

from movesic.engines.api import Engine, Playlist

scope = "user-library-read"


class Spotify(Engine):
    def __init__(self, client_id, client_secret):
        # auth_manager = SpotifyClientCredentials(client_id, client_secret)
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=f"http://localhost:44444/",
            scope=scope,
            # open_browser=False,
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        # self.auth_manager = SpotifyOAuth(client_id, client_secret, scope=scope)

    def auth(self):
        pass

    def get_playlists(self):
        query_result = self.sp.current_user_playlists()
        result = []
        for item in query_result["items"]:
            result.append(
                Playlist(
                    name=item["name"],
                    external_url=item["external_urls"]["spotify"],
                )
            )
        return result

    def get_songs(self, playlist):
        # for idx, item in enumerate(results['items']):
        #     track = item['track']
        #     print(idx, track['artists'][0]['name'], " – ", track['name'])
        pass

    def find_song(self, name):
        pass
