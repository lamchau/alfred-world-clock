from __future__ import annotations

import os


class Cache:
    def __init__(self, cachedir: str):
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        self.cachedir = cachedir

    def download_image(self, url: str, filename: str | None = None) -> str:
        import requests  # lazy import — only loaded when actually downloading

        filename = filename if filename else url.split("/")[-1]
        path = f"{self.cachedir}/{filename}"

        if os.path.isfile(path):
            return path

        with open(path, "wb") as f:
            f.write(requests.get(url).content)

        return path
