import os
import pytest
from spotipy import CacheFileHandler
from movesic.engines.youtube import Youtube
from movesic.engines.spotify import Spotify


YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_SECRET = os.getenv("YOUTUBE_SECRET")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")


@pytest.fixture(scope="session")
def youtube():
    engine = Youtube(
        "tests/oauth.json",
        client_id=YOUTUBE_CLIENT_ID,
        secret=YOUTUBE_SECRET,
    )
    yield engine


@pytest.fixture(scope="session")
def spotify():
    engine = Spotify(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_SECRET,
        CacheFileHandler("tests/.cache"),
    )
    yield engine
