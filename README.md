# MoveSIC

Sync your music playlists between different services.

## Supported services:

- Youtube Music (via [ytmusicapi](https://github.com/sigma67/ytmusicapi))
- Spotify (via [spotipy](https://github.com/spotipy-dev/spotipy))

## Development

- Prerequisites:

    - for Debian:
        ```bash
        sudo apt install python3-dev libcairo2-dev libxt-dev libgirepository-2.0-dev
        ```

- use [`uv`](https://docs.astral.sh/uv)
    ```bash
    uv sync
    ```
    or, if you want to build native desktop app
    ```bash
    uv sync --extra native
    ```

###

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
