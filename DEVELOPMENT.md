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
