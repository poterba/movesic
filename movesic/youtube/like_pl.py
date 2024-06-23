# macOS packaging support
from multiprocessing import freeze_support  # noqa

freeze_support()  # noqa

from ytmusicapi import YTMusic
import logging
import time


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
