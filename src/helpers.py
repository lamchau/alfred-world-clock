from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from pyflow import Workflow

import formatters


def get_formatter(workflow: Workflow) -> callable:
    timestamp_format = workflow.env.get("TIMESTAMP_FORMAT", "FORMAT_DEFAULT")
    if timestamp_format == "FORMAT_CUSTOM":
        fmt = workflow.env.get("TIMESTAMP_FORMAT_CUSTOM", "%H:%M:%S (%B %d, %Y)")
        return formatters.custom(fmt)
    return formatters.FORMATTERS[timestamp_format]


def get_icon(timezone: str, now: datetime, home_tz: str) -> str:
    if timezone == home_tz:
        return "img/icons/home.png"

    if timezone == "UTC":
        return "img/icons/utc.png"

    utc_offset = now.utcoffset()
    utc_offset_hours = round(utc_offset.days * 24 + utc_offset.seconds / 60 / 60)
    return f"img/icons/{utc_offset_hours}.png"


def get_home(workflow: Workflow) -> tuple[str, datetime]:
    home_tz = workflow.env["HOME"][3:].replace("__", "/")

    home_now = datetime.now(timezone.utc).astimezone(ZoneInfo(home_tz))

    return home_tz, home_now


def get_name_replacements(workflow: Workflow) -> dict[str, str]:
    sep = "//"

    name_replacements = {}

    for line in workflow.env.get("NAME_REPLACEMENTS", "").split("\n"):
        if not line:
            continue

        if sep not in line:
            raise ValueError(f"name replacement '{line}' is missing the '{sep}' separator.")

        parts = line.split(sep)

        if len(parts) != 2:
            raise ValueError(f"name replacement '{line}' should have the format `old {sep} new`.")

        if "" in parts:
            raise ValueError(f"name replacement '{line}' should have the format `old {sep} new`.")

        old, new = parts
        name_replacements[old.strip()] = new.strip()

    return name_replacements


def get_timezones(workflow: Workflow, now: datetime, include: list[str] | None = None) -> dict[str, datetime]:
    timezones = set(
        map(
            lambda item: item[0][3:].replace("__", "/"),
            filter(
                lambda item: item[0].startswith("TZ_") and item[1] == "1",
                workflow.env.items(),
            ),
        )
    )

    timezones.update(include or [])

    return {
        tz_name: now.replace(
            tzinfo=timezone.utc,
        ).astimezone(
            ZoneInfo(tz_name),
        )
        for tz_name in timezones
    }


def get_home_offset_str(timezone: str, home_tz: str, now: datetime, home_now: datetime, utc: bool = False) -> str:
    utc_offset = get_utc_offset(now)

    if utc_offset == 0:
        utc_offset_str = "UTC"
    elif utc_offset > 0:
        utc_offset_str = f"UTC +{utc_offset}"
    else:
        utc_offset_str = f"UTC {utc_offset}"

    if timezone == home_tz:
        return f"({utc_offset_str})"

    now_tmp = now.replace(tzinfo=None)
    home_now_tmp = home_now.replace(tzinfo=None)

    if home_now_tmp > now_tmp:
        home_offset = home_now_tmp - now_tmp
        seconds = home_offset.seconds + 1
        text = "behind"
    else:
        home_offset = home_now_tmp - now_tmp
        seconds = 24 * 60 * 60 - home_offset.seconds + 1
        text = "ahead of"

    if not utc:
        return "({utc_offset}) · [{hours:02}:{minutes:02} hs {text} home 🏠]".format(
            hours=seconds // 3600,
            minutes=(seconds % 3600) // 60,
            text=text,
            utc_offset=utc_offset_str,
        )
    else:
        return "({utc_offset})".format(
            utc_offset=utc_offset_str,
        )


def get_utc_offset(now: datetime) -> int:
    utc_offset = now.utcoffset()

    return round(utc_offset.days * 24 + utc_offset.seconds / 60 / 60)
