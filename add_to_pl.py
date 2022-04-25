
from ytmusicapi import YTMusic
import logging
import coloredlogs
import inquirer

def sort_songs():
    results = []
    with open('vk.txt', 'r') as f:
        results = f.readlines()
    songs = []
    for _, artist, song in (results[i:i+3] for i in range(0,len(results),3)):
    # for _, artist, song in results:
        songs.append("{} - {}".format(artist.strip(), song.strip()))
    return songs

def song_entry_to_string(yt_song_entry):
    artists = map(lambda x: x['name'], yt_song_entry['artists'])
    return '{} - {}'.format(','.join(artists), yt_song_entry['title'])

def ask_song_variant(song, yt, filter_tag):
    search_results = yt.search(song, filter=filter_tag, ignore_spelling=True)
    options = list(map(song_entry_to_string, search_results[:5]))
    options.insert(0,None)
    questions = [
        inquirer.List(
            "choice",
            message="What to add from {} `{}` ()".format(filter_tag, song),
            choices=options,
        ),
    ]
    result = inquirer.prompt(questions, theme=inquirer.themes.GreenPassion(), raise_keyboard_interrupt=True)
    choice = result['choice']
    return search_results[options.index(choice) - 1] if choice else None

def main():
    ytmusic = YTMusic(auth="headers_auth.json")

    playlists = ytmusic.get_library_playlists()
    vk_pl = next(filter(lambda x: x['title']=='VK', playlists), None)
    logging.info('Found playlist {}'.format(vk_pl['description']))

    songs = sort_songs()
    for idx, song in enumerate(songs):
        result = ask_song_variant(song, ytmusic, 'songs')
        if not result:
            result = ask_song_variant(song, ytmusic, 'videos')
        if not result:
            logging.warning('Skipping {}'.format(song))
            continue
        ytmusic.add_playlist_items(vk_pl['playlistId'], [result['videoId']])
        logging.info('added {}/{} {}'.format(idx, len(songs), song_entry_to_string(result)))

if __name__ == '__main__':
    coloredlogs.install(level=logging.INFO)
    try:
        main()
    except Exception as e:
        logging.exception(e)
    except KeyboardInterrupt as e:
        logging.error('KeyboardInterrupt')
