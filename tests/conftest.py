import os
import pytest
from spotipy import CacheFileHandler
from movesic.engines.youtube import Youtube
from movesic.engines.spotify import Spotify


YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_SECRET = os.getenv("YOUTUBE_SECRET")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")


def youtube():
    return Youtube(
        "tests/oauth.json",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_SECRET,
    )


def spotify():
    return Spotify(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_SECRET,
        CacheFileHandler("tests/.cache"),
    )


@pytest.fixture(scope="function")
def engine(request):
    yield request.param()
