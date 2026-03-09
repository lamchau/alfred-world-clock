from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pyflow import Workflow

import data
import formatters
import helpers


# parse parameter to a set of valid time formats
def convert_to_time(time_arg: str) -> tuple[int, int, int]:
    for format_str in ["%H:%M:%S", "%H:%M", "%I:%M%p", "%I%p", "%I:%M %p", "%I %p"]:
        try:
            time = datetime.strptime(time_arg.upper(), format_str)
            return time.hour, time.minute, time.second
        except ValueError:
            pass

    raise ValueError(
        f"'{time_arg}' should follow the formats 'HH:MM', 'HH:MM:SS', '5pm', or '5:30pm'"
    )


# parse parameter to a set of valid date formats
def convert_to_date(date_arg: str) -> tuple[int, int, int]:
    for format_str in ["%d/%m/%Y", "%Y-%m-%d"]:
        try:
            date = datetime.strptime(date_arg, format_str)
            return date.day, date.month, date.year
        except ValueError:
            pass

    raise ValueError(f"'{date_arg}' should follow the formats 'dd/mm/yyyy' or 'yyyy-mm-dd'")


_TIMEPARSE_RE = re.compile(
    r"""
    (?:(\d+(?:\.\d+)?)\s*h(?:(?:ou)?rs?)?)?\s*  # hours: 3h, 3.5h, 3hr, 3hrs, 3hours
    (?:(\d+(?:\.\d+)?)\s*m(?:in(?:ute)?s?)?)?\s* # minutes: 30m, 1.5m, 30min, 30minutes
    (?:(\d+(?:\.\d+)?)\s*s(?:ec(?:ond)?s?)?)?     # seconds: 90s, 90sec, 90seconds
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

# matches H:MM or HH:MM as a duration (distinguished from clock time by context)
_DURATION_COLON_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def timeparse(s: str) -> float | None:
    """parse a duration string into total seconds.

    supports:
      3h, 3.5h, 1h30m, 90s, 2hours, 45min, 1h30m15s
      3:30 (3 hours 30 minutes as H:MM)
      with sign prefix: +3h, -1h30m, +3:30
    """
    s = s.lstrip("+-").strip()

    # try H:MM colon format first
    colon_match = _DURATION_COLON_RE.match(s)
    if colon_match:
        hours = int(colon_match.group(1))
        minutes = int(colon_match.group(2))
        return hours * 3600 + minutes * 60

    # try unit-based format (3h, 1.5h, 30m, etc.)
    m = _TIMEPARSE_RE.match(s)
    if not m or not any(m.groups()):
        return None
    hours = float(m.group(1) or 0)
    minutes = float(m.group(2) or 0)
    seconds = float(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def is_duration(s: str) -> bool:
    """check if a string looks like a time duration with a unit suffix.

    matches: 3h, 3.5h, 30m, 1h30m, 90s
    does NOT match bare colon form (3:30) since that's ambiguous with clock time.
    colon durations are only valid with a sign prefix (+3:30, -3:30).
    """
    stripped = s.lstrip("+-").strip()
    # colon form without sign prefix is clock time, not duration
    if _DURATION_COLON_RE.match(stripped):
        return False
    return timeparse(s) is not None


# parse a positive or negative time offset to create a delta in seconds
def convert_to_delta(delta_arg: str) -> timedelta:
    seconds = timeparse(delta_arg)
    if seconds is None:
        raise ValueError("invalid time offset")
    sign = -1 if delta_arg.startswith("-") else 1
    return timedelta(seconds=sign * seconds)


# parse arguments to find in which mode the workflow is running (always returns utc datetime)
def parse_args(args: list[str], home_now: datetime) -> datetime:
    if len(args) > 2:
        raise ValueError("too many params, expected: [+offset] / [-offset] / [time] / [time date]")

    # mode now: shows current time
    if len(args) == 0:
        return datetime.now(timezone.utc)

    # mode offset: shows current time +/- a time offset
    if args[0][0] in "+-":
        return datetime.now(timezone.utc) + convert_to_delta(args[0])

    # mode offset (bare duration): treat "3h", "1h30m" etc. as positive offset
    if is_duration(args[0]):
        return datetime.now(timezone.utc) + convert_to_delta(args[0])

    # mode set: shows especific date and time as home
    hour, minute, second = convert_to_time(args[0])

    now = home_now.replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=0,
    )

    if len(args) == 2:
        day, month, year = convert_to_date(args[1])

        now = now.replace(
            day=day,
            month=month,
            year=year,
        )

    return now.astimezone(timezone.utc)


def main(workflow: Workflow):
    name_replacements = helpers.get_name_replacements(workflow)
    formatter = helpers.get_formatter(workflow)

    home_tz, home_now = helpers.get_home(workflow)
    utc_now = parse_args(workflow.args, home_now)

    timezones = helpers.get_timezones(
        workflow,
        utc_now,
        include=[home_tz],
    )

    for tz_name, now in sorted(timezones.items(), key=lambda kw: kw[1].isoformat()):
        location = tz_name.split("/")[-1].replace("_", " ")
        location = name_replacements.get(location, location)

        meeting_arg = json.dumps({
            "iso": now.isoformat(),
            "tz": tz_name,
            "location": location,
        })

        workflow.new_item(
            title=formatter(now),
            subtitle="{flag} {location} {home_offset}".format(
                flag=data.flags.get(tz_name, "\U0001f310"),
                location=location,
                home_offset=helpers.get_home_offset_str(
                    timezone=tz_name,
                    home_tz=home_tz,
                    now=now,
                    home_now=home_now,
                ),
            ),
            arg="{now} {flag} {location} {home_offset}".format(
                now=formatter(now),
                flag=data.flags.get(tz_name, "\U0001f310"),
                location=location,
                home_offset=helpers.get_home_offset_str(
                    timezone=tz_name,
                    home_tz=home_tz,
                    now=now,
                    home_now=home_now,
                    utc=True,
                ),
            ),
            copytext=formatter(now),
            valid=True,
            uid=str(uuid4()),
        ).set_icon_file(
            path=helpers.get_icon(tz_name, now, home_tz),
        ).set_cmd_mod(
            subtitle="\U0001f4c5 Create meeting (default calendar)",
            arg=meeting_arg,
            variables={"calendar": "default"},
        ).set_alt_mod(
            subtitle="\U0001f4c5 Create meeting (other calendar)",
            arg=meeting_arg,
            variables={"calendar": "other"},
        ).set_ctrl_mod(
            subtitle="Copy ISO format (with microseconds)",
            arg=formatters.iso8601(now),
        ).set_shift_mod(
            subtitle="Copy ISO format (without microseconds)",
            arg=formatters.iso8601_without_microseconds(now),
        )


if __name__ == "__main__":
    wf = Workflow()
    wf.run(main)
    wf.send_feedback()
    sys.exit()
