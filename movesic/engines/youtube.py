import logging

from ytmusicapi import YTMusic
from movesic.engines.api import Engine


class Youtube(Engine):
    def __init__(self):
        self.ytmusic = YTMusic(auth="headers_auth.json")

    def get_playlists():
        pass

    def get_songs():
        pass

    def find_song():
        pass


# old stuff to analyze


def sort_songs():
    results = []
    with open("vk.txt", "r") as f:
        results = f.readlines()
    songs = []
    for _, artist, song in (results[i : i + 3] for i in range(0, len(results), 3)):
        # for _, artist, song in results:
        songs.append("{} - {}".format(artist.strip(), song.strip()))
    return songs


def song_entry_to_string(yt_song_entry):
    artists = map(lambda x: x["name"], yt_song_entry["artists"])
    return "{} - {}".format(",".join(artists), yt_song_entry["title"])


def ask_song_variant(song, yt, filter_tag):
    search_results = yt.search(song, filter=filter_tag, ignore_spelling=True)
    options = list(map(song_entry_to_string, search_results[:5]))
    options.insert(0, None)


def main():
    ytmusic = YTMusic(auth="headers_auth.json")

    playlists = ytmusic.get_library_playlists()
    vk_pl = next(filter(lambda x: x["title"] == "VK", playlists), None)
    logging.info("Found playlist {}".format(vk_pl["description"]))

    songs = sort_songs()
    for idx, song in enumerate(songs):
        result = ask_song_variant(song, ytmusic, "songs")
        if not result:
            result = ask_song_variant(song, ytmusic, "videos")
        if not result:
            logging.warning("Skipping {}".format(song))
            continue
        ytmusic.add_playlist_items(vk_pl["playlistId"], [result["videoId"]])
        logging.info(
            "added {}/{} {}".format(idx, len(songs), song_entry_to_string(result))
        )


def main():
    ytmusic = YTMusic(auth="headers_auth.json")

    playlists = ytmusic.get_library_playlists()
    vk_pl = next(filter(lambda x: x["title"] == "VK", playlists), None)
    logging.info("Found playlist {}".format(vk_pl["playlistId"]))

    all_songs = ytmusic.get_playlist(vk_pl["playlistId"], limit=2000)
    songs = list(filter(lambda x: x["likeStatus"] != "LIKE", all_songs["tracks"]))
    len_songs = len(songs)
    logging.info("Found {} unliked songs in it, fixing".format(len_songs))

    for idx, song in enumerate(songs):
        result = ytmusic.rate_song(song["videoId"], rating="LIKE")
        runs = result["actions"][0]["addToToastAction"]["item"][
            "notificationActionRenderer"
        ]["responseText"]["runs"]
        logging.info(
            "{}/{} {}: {}".format(idx, len_songs, runs[0]["text"], song["title"])
        )
