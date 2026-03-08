"""download latest IANA timezone data, regenerate src/data.py and update info.plist.

usage: python3 tzdata/update.py
  or:  just update-tz
"""
from __future__ import annotations

import csv
import io
import plistlib
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

TZDATA_DIR = Path(__file__).parent
ROOT_DIR = TZDATA_DIR.parent
PLIST_PATH = ROOT_DIR / "info.plist"
DATA_PY_PATH = ROOT_DIR / "src" / "data.py"
TZDATA_URL = "https://data.iana.org/time-zones/tzdata-latest.tar.gz"


def country_code_to_emoji(code: str) -> str:
    """convert 2-letter country code to flag emoji (regional indicator symbols)."""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


def parse_iso3166_tab(content: str) -> list[tuple[str, str]]:
    """parse iso3166.tab into (country_code, country_name) pairs."""
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0], parts[1]))
    return rows


def parse_zone_tab(content: str) -> list[tuple[str, str]]:
    """parse zone1970.tab into (timezone, country_code) pairs."""
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            # zone1970.tab: country_codes, coordinates, timezone, ...
            country_codes = parts[0]
            tz_name = parts[2]
            # use first country code for shared zones
            country_code = country_codes.split(",")[0]
            rows.append((tz_name, country_code))
    return rows


def format_offset(offset_hours: float) -> str:
    if offset_hours == 0:
        return "UTC"
    sign = "+" if offset_hours > 0 else ""
    if offset_hours == int(offset_hours):
        return f"UTC {sign}{int(offset_hours)}"
    hours = int(offset_hours)
    minutes = int(abs(offset_hours - hours) * 60)
    return f"UTC {sign}{hours}:{minutes:02d}"


def get_utc_offset_hours(tz_name: str) -> float:
    now = datetime.now(timezone.utc).astimezone(ZoneInfo(tz_name))
    offset = now.utcoffset()
    return offset.total_seconds() / 3600


def download_tzdata() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """download and parse latest IANA tzdata. returns (countries, timezones)."""
    print(f"downloading {TZDATA_URL}...")
    with urlopen(TZDATA_URL) as response:
        data = response.read()

    print("extracting...")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        iso3166 = tar.extractfile("iso3166.tab")
        if iso3166 is None:
            raise RuntimeError("iso3166.tab not found in tarball")
        countries = parse_iso3166_tab(iso3166.read().decode("utf-8"))

        zone_tab = tar.extractfile("zone1970.tab")
        if zone_tab is None:
            raise RuntimeError("zone1970.tab not found in tarball")
        timezones = parse_zone_tab(zone_tab.read().decode("utf-8"))

    return countries, timezones


def save_csvs(
    countries: list[tuple[str, str]],
    timezones: list[tuple[str, str]],
) -> None:
    """save parsed data to csv files."""
    country_path = TZDATA_DIR / "country.csv"
    with open(country_path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in sorted(countries, key=lambda r: r[0]):
            writer.writerow(row)
    print(f"  {country_path.name}: {len(countries)} countries")

    time_zone_path = TZDATA_DIR / "time_zone.csv"
    with open(time_zone_path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in sorted(timezones, key=lambda r: r[0]):
            writer.writerow(row)
    print(f"  {time_zone_path.name}: {len(timezones)} timezones")


def generate_data_py(
    countries: list[tuple[str, str]],
    timezones: list[tuple[str, str]],
) -> None:
    """regenerate src/data.py with pre-computed timezone -> flag emoji mapping."""
    country_map = dict(countries)
    flags: dict[str, str] = {}
    for tz_name, country_code in timezones:
        if tz_name not in flags:
            flags[tz_name] = country_code_to_emoji(country_code)

    lines = [
        "# pre-computed timezone -> country flag emoji mapping",
        "#",
        "# baked into a dict literal to avoid import-time overhead.",
        "# the original approach (iterating pytz.country_timezones at import)",
        "# added ~78ms to every alfred invocation. a dict literal loads in <1ms",
        "# since python compiles it to .pyc bytecode.",
        "#",
        f"# {len(flags)} timezones from {len(set(dict(timezones).values()))} countries",
        "# regenerate with: just update-tz",
        "FLAGS = {",
    ]
    for tz_name in sorted(flags):
        lines.append(f'    "{tz_name}": "{flags[tz_name]}",')
    lines.append("}")
    lines.append("")
    lines.append("# backward-compatible alias")
    lines.append("flags = FLAGS")
    lines.append("")

    DATA_PY_PATH.write_text("\n".join(lines))
    print(f"  data.py: {len(flags)} timezone flags")


def update_plist(
    countries: list[tuple[str, str]],
    timezones: list[tuple[str, str]],
) -> None:
    """update info.plist timezone checkboxes and home dropdown, sorted by utc offset."""
    country_map = dict(countries)

    # collect unique timezones with metadata
    seen: set[str] = set()
    entries: list[tuple[float, str, str, str, str]] = []
    for tz_name, country_code in timezones:
        if tz_name in seen:
            continue
        seen.add(tz_name)

        country_name = country_map.get(country_code, country_code)
        flag = country_code_to_emoji(country_code)
        city_name = tz_name.split("/")[-1].replace("_", " ")
        offset_hours = get_utc_offset_hours(tz_name)
        entries.append((offset_hours, country_name, city_name, flag, tz_name))

    # sort by utc offset, then country, then city
    entries.sort(key=lambda e: (e[0], e[1], e[2]))

    # build checkbox dicts and home pairs
    checkboxes: list[dict] = []
    home_pairs: list[list[str]] = []
    for offset_hours, country_name, city_name, flag, tz_name in entries:
        offset_str = format_offset(offset_hours)
        label = f"{flag} ({offset_str}) {country_name} / {city_name}"
        variable = f"TZ_{tz_name.replace('/', '__')}"

        checkboxes.append({
            "config": {
                "default": False,
                "required": False,
                "text": label,
            },
            "description": "",
            "label": "",
            "type": "checkbox",
            "variable": variable,
        })
        home_pairs.append([label, variable])

    # update info.plist
    with open(PLIST_PATH, "rb") as f:
        plist = plistlib.load(f)

    config = plist["userconfigurationconfig"]

    # find HOME popup and first timezone checkbox dynamically
    home_index = None
    checkbox_start = None
    for i, item in enumerate(config):
        if item.get("variable") == "HOME":
            home_index = i
        if checkbox_start is None and item.get("type") == "checkbox" and item.get("variable", "").startswith("TZ_"):
            checkbox_start = i

    if home_index is None:
        raise RuntimeError("HOME popup not found in info.plist")
    if checkbox_start is None:
        raise RuntimeError("no TZ_ checkbox found in info.plist")

    config[checkbox_start:] = checkboxes
    config[home_index]["config"]["pairs"] = home_pairs

    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f, fmt=plistlib.FMT_BINARY)

    print(f"  info.plist: {len(checkboxes)} checkboxes, {len(home_pairs)} home options")
    print(f"  sorted by utc offset")


def main():
    countries, timezones = download_tzdata()
    save_csvs(countries, timezones)
    generate_data_py(countries, timezones)
    update_plist(countries, timezones)
    print("done")


if __name__ == "__main__":
    main()
