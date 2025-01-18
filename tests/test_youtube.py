import logging


def test_read(youtube, caplog):
    caplog.set_level(logging.DEBUG)
    _info = youtube.info()
    playlists = youtube.get_playlists()
    for pl in playlists:
        songs = youtube.get_songs(pl)
        logging.debug(len(songs))


def test_find_song(youtube):
    song = youtube.find_song("Lotus Flower", "Radiohead")
    print(song)
