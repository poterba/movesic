import logging

import pytest

from movesic.engines import api
from tests.conftest import spotify, youtube


@pytest.mark.parametrize("engine", [spotify, youtube], indirect=True)
def test_read(engine: api.Engine, caplog):
    caplog.set_level(logging.DEBUG)
    _info = engine.info()
    playlists = engine.get_playlists()
    for pl in playlists:
        songs = engine.get_songs(pl)
        logging.debug(len(songs))


@pytest.mark.parametrize("engine", [spotify, youtube], indirect=True)
def test_find_song(engine: api.Engine, caplog):
    caplog.set_level(logging.DEBUG)
    _song = engine.find_song("Paranoid Android", "Radiohead")
    print(_song)


@pytest.mark.parametrize("engine", [spotify, youtube], indirect=True)
def test_write(engine: api.Engine, caplog):
    caplog.set_level(logging.DEBUG)
    _playlist = engine.add_playlist("TEST")
    _songs = engine.find_song("Paranoid Android", "Radiohead")
    engine.add_song_to_playlist(_songs[0], _playlist)
    _result = engine.delete_playlist(_playlist)
    print(_result)
