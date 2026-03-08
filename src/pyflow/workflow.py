from __future__ import annotations

import json
import logging
import os
import sys

from .cache import Cache
from .icon import Icon
from .item import Item


class Workflow:
    def __init__(self):
        self._cache: Cache | None = None
        self._env: dict[str, str] | None = None
        self._items: list[dict] = []

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel((logging.INFO, logging.DEBUG)[self.debugging])

    @property
    def args(self) -> list[str]:
        return sys.argv[1:]

    @property
    def env(self) -> dict[str, str]:
        if self._env is None:
            self._env = dict(os.environ)
        return self._env

    @property
    def bundleid(self) -> str:
        return self.env["alfred_workflow_bundleid"]

    @property
    def debugging(self) -> bool:
        return self.env.get("alfred_debug") == "1"

    @property
    def name(self) -> str:
        return self.env["alfred_workflow_name"]

    @property
    def version(self) -> str:
        return self.env["alfred_workflow_version"]

    @property
    def cache(self) -> Cache:
        if self._cache is None:
            self._cache = Cache(self.cachedir)
        return self._cache

    @property
    def cachedir(self) -> str:
        return self.env["alfred_workflow_cache"]

    @property
    def workflowdir(self) -> str:
        return os.getenv("PWD")

    def new_item(self, **kwargs) -> Item:
        return self.add_item(Item(**kwargs))

    def add_item(self, item: Item) -> Item:
        item.cache = self.cache
        self._items.append(item)
        return item

    def run(self, func):
        try:
            func(self)
        except Exception as e:
            self.logger.exception(e)
            self.new_item(
                title=str(e),
                subtitle=f"Error while running workflow '{self.name}:v{self.version}'",
            ).set_icon_builtin(icon=Icon.ALERT_STOP)

    def send_feedback(self, indent: int = 2):
        json.dump(self.serialized, sys.stdout, indent=indent)
        sys.stdout.flush()

    @property
    def serialized(self) -> dict:
        return {
            "items": [item.serialized for item in self._items],
        }
