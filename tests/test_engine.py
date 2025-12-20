import logging

import pytest

from movesic.engines import api
from tests.conftest import spotify, youtube

_TEST_SONG = ("TERRITORY", "The Blaze")


@pytest.mark.parametrize("engine", [spotify, youtube], indirect=True)
def test_read(engine: api.Engine, caplog):
    caplog.set_level(logging.DEBUG)
    _info = engine.info()
    playlists = engine.get_playlists()
    for pl in playlists:
        songs = engine.get_songs(pl)
        logging.debug(len(songs))
        assert isinstance(songs, list)  # Ensure songs is a list


@pytest.mark.parametrize("engine", [spotify, youtube], indirect=True)
def test_find_song(engine: api.Engine, caplog):
    caplog.set_level(logging.DEBUG)
    _song = engine.find_song(*_TEST_SONG)
    assert _song is not None  # Ensure a song is found
    assert isinstance(_song, list)  # Ensure the result is a list
    assert len(_song) > 0  # Ensure the list is not empty


@pytest.mark.parametrize("engine", [spotify, youtube], indirect=True)
def test_write(engine: api.Engine, caplog):
    caplog.set_level(logging.DEBUG)
    _playlist = engine.add_playlist("TEST")
    _songs = engine.find_song(*_TEST_SONG)
    assert isinstance(_songs, list)  # Ensure the result is a list
    assert len(_songs) > 0  # Ensure the list is not empty
    engine.add_song_to_playlist(_songs[0], _playlist)
    _result = engine.delete_playlist(_playlist)
    assert _result is True  # Ensure the playlist is deleted successfully
