"""Create a calendar meeting from World Clock timezone data.

Called by Alfred as a Run Script action.
Receives JSON via stdin: {"iso": "...", "tz": "...", "location": "..."}
Reads env vars: DEFAULT_APP, OTHER_APP, MEETING_DURATION, calendar

Outlook-like apps: generates a temporary .ics file and opens it.
Browser apps: opens a pre-filled Google Calendar URL.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import uuid4

# apps that handle .ics files natively (not browsers)
ICS_APPS = {"Microsoft Outlook"}


def build_gcal_url(start: datetime, end: datetime, title: str, tz: str) -> str:
    """Build a Google Calendar event creation URL.

    Uses local time format (no Z suffix) with the ctz parameter
    so Google Calendar interprets the times in the correct timezone.
    """
    fmt = "%Y%m%dT%H%M%S"
    return (
        "https://calendar.google.com/calendar/render"
        "?action=TEMPLATE"
        f"&text={quote(title)}"
        f"&dates={start.strftime(fmt)}/{end.strftime(fmt)}"
        f"&ctz={quote(tz)}"
    )


def build_ics(start: datetime, end: datetime, title: str, tz: str) -> str:
    """Build an iCalendar (.ics) string for a single event."""
    utc_fmt = "%Y%m%dT%H%M%SZ"
    start_utc = start.astimezone(tz=timezone.utc)
    end_utc = end.astimezone(tz=timezone.utc)
    uid = str(uuid4())
    now_utc = datetime.now(tz=timezone.utc)

    # .ics spec requires CRLF line endings
    return f"""\
BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//World Clock//Alfred Workflow//EN\r
BEGIN:VEVENT\r
UID:{uid}\r
DTSTAMP:{now_utc.strftime(utc_fmt)}\r
DTSTART:{start_utc.strftime(utc_fmt)}\r
DTEND:{end_utc.strftime(utc_fmt)}\r
SUMMARY:{title}\r
END:VEVENT\r
END:VCALENDAR\r
"""


def open_meeting(start: datetime, duration_min: int, title: str, tz: str, app: str) -> None:
    """Open a meeting in the specified app.

    For ICS_APPS (e.g. Outlook): generates a .ics file and opens it.
    For browsers (e.g. Chrome, Edge): opens a Google Calendar URL.
    """
    end = start + timedelta(minutes=duration_min)

    if app in ICS_APPS:
        ics_content = build_ics(start, end, title, tz)
        ics_path = os.path.join(tempfile.gettempdir(), f"world-clock-{uuid4().hex[:8]}.ics")
        with open(ics_path, "w") as f:
            f.write(ics_content)
        subprocess.run(["open", "-a", app, ics_path], check=False)
    else:
        url = build_gcal_url(start, end, title, tz)
        subprocess.run(["open", "-a", app, url], check=False)


def main() -> None:
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    data = json.loads(raw)
    start = datetime.fromisoformat(data["iso"])
    tz_name: str = data["tz"]
    location: str = data["location"]

    default_app = os.environ.get("DEFAULT_APP", "Microsoft Outlook")
    other_app = os.environ.get("OTHER_APP", "Google Chrome")
    duration = int(os.environ.get("MEETING_DURATION", "30"))

    # "default" or "other" — set via Alfred modifier variables
    choice = os.environ.get("calendar", "default")
    app = default_app if choice == "default" else other_app

    title = f"Meeting ({location})"
    open_meeting(start, duration, title, tz_name, app)


if __name__ == "__main__":
    main()
