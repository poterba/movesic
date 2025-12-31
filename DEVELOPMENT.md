#

Prerequisites:

- for Debian:
    ```bash
    sudo apt install python3-dev libcairo2-dev libxt-dev libgirepository-2.0-dev
    ```

---

use [`uv`](https://docs.astral.sh/uv)
```bash
uv sync
```
or, if you want to build native desktop app
```bash
uv sync --extra native
```

---

Tests are written in a way, where you should pass preregistered app values via environment variables:

```ini filename=.env
YOUTUBE_CLIENT_ID=
YOUTUBE_SECRET=
SPOTIFY_CLIENT_ID=
SPOTIFY_SECRET=
DEEZER_CLIENT_ID=
DEEZER_SECRET=
```
