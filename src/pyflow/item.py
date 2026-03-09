from __future__ import annotations

import typing
from uuid import uuid4

from .icon import Icon

if typing.TYPE_CHECKING:
    from .cache import Cache


class Item:
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        valid: bool = True,
        arg: str | None = None,
        autocomplete: str | None = None,
        copytext: str | None = None,
        largetype: str | None = None,
        match: str | None = None,
        quicklookurl: str | None = None,
        uid: str | None = None,
        type: str = "default",
    ):
        self.title = title
        self.subtitle = subtitle
        self.valid = valid
        self.arg = arg
        self.autocomplete = autocomplete
        self.copytext = copytext
        self.largetype = largetype
        self.match = match
        self.quicklookurl = quicklookurl
        self.uid = uid or str(uuid4())
        self.type = type

        self.cache: Cache | None = None

        self._icon: dict = {}
        self._mods: dict = {}

    def set_icon_builtin(self, icon: Icon) -> Item:
        return self.set_icon_file(path=str(icon))

    def set_icon_file(self, path: str) -> Item:
        self._icon = {
            "path": path,
            "type": None,
        }
        return self

    def set_icon_url(self, url: str, filename: str | None = None) -> Item:
        return self.set_icon_file(
            path=self.cache.download_image(url=url, filename=filename),
        )

    def _set_mod(
        self,
        name: str,
        arg: str | None = None,
        subtitle: str | None = None,
        valid: bool = True,
        variables: dict[str, str] | None = None,
    ) -> Item:
        mod: dict = {
            "arg": arg,
            "subtitle": subtitle,
            "valid": valid,
        }
        if variables:
            mod["variables"] = variables
        self._mods[name] = mod
        return self

    def set_alt_mod(
        self,
        arg: str | None = None,
        subtitle: str | None = None,
        valid: bool = True,
        variables: dict[str, str] | None = None,
    ) -> Item:
        return self._set_mod("alt", arg=arg, subtitle=subtitle, valid=valid, variables=variables)

    def set_cmd_mod(
        self,
        arg: str | None = None,
        subtitle: str | None = None,
        valid: bool = True,
        variables: dict[str, str] | None = None,
    ) -> Item:
        return self._set_mod("cmd", arg=arg, subtitle=subtitle, valid=valid, variables=variables)

    def set_ctrl_mod(
        self,
        arg: str | None = None,
        subtitle: str | None = None,
        valid: bool = True,
        variables: dict[str, str] | None = None,
    ) -> Item:
        return self._set_mod("ctrl", arg=arg, subtitle=subtitle, valid=valid, variables=variables)

    def set_shift_mod(
        self,
        arg: str | None = None,
        subtitle: str | None = None,
        valid: bool = True,
        variables: dict[str, str] | None = None,
    ) -> Item:
        return self._set_mod("shift", arg=arg, subtitle=subtitle, valid=valid, variables=variables)

    @property
    def serialized(self) -> dict:
        return {
            "arg": self.arg,
            "autocomplete": self.autocomplete,
            "icon": self._icon,
            "match": self.match,
            "mods": self._mods,
            "quicklookurl": self.quicklookurl,
            "subtitle": self.subtitle,
            "text": {
                "copy": self.copytext,
                "largetype": self.largetype,
            },
            "title": self.title,
            "uid": self.uid,
            "type": self.type,
            "valid": self.valid,
        }
