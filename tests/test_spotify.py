import logging


def test_read(spotify, caplog):
    caplog.set_level(logging.DEBUG)
    playlists = spotify.get_playlists()
    for pl in playlists:
        songs = spotify.get_songs(pl)
        logging.debug(len(songs))


def test_find_song(spotify, caplog):
    caplog.set_level(logging.DEBUG)
    song = spotify.find_song("Lotus Flower", "Radiohead")
    print(song)
