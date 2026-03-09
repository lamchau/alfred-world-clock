from datetime import datetime
from zoneinfo import ZoneInfo

from create_meeting import build_gcal_url, build_ics


class TestBuildGcalUrl:
    def test_basic_url_structure(self):
        start = datetime(2026, 3, 8, 14, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        end = datetime(2026, 3, 8, 15, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        url = build_gcal_url(start, end, "Meeting (Tokyo)", "Asia/Tokyo")

        assert url.startswith("https://calendar.google.com/calendar/render")
        assert "action=TEMPLATE" in url
        assert "Meeting" in url
        assert "20260308T143000" in url
        assert "20260308T150000" in url
        assert "ctz=Asia/Tokyo" in url

    def test_title_encoding(self):
        start = datetime(2026, 3, 8, 10, 0, tzinfo=ZoneInfo("America/New_York"))
        end = datetime(2026, 3, 8, 10, 30, tzinfo=ZoneInfo("America/New_York"))
        url = build_gcal_url(start, end, "Meeting (New York)", "America/New_York")

        assert "Meeting%20%28New%20York%29" in url

    def test_different_timezone(self):
        start = datetime(2026, 6, 15, 9, 0, tzinfo=ZoneInfo("Europe/London"))
        end = datetime(2026, 6, 15, 9, 30, tzinfo=ZoneInfo("Europe/London"))
        url = build_gcal_url(start, end, "Standup", "Europe/London")

        assert "ctz=Europe/London" in url
        assert "20260615T090000" in url


class TestBuildIcs:
    def test_valid_vcalendar_structure(self):
        start = datetime(2026, 3, 8, 14, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        end = datetime(2026, 3, 8, 15, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        ics = build_ics(start, end, "Meeting (Tokyo)", "Asia/Tokyo")

        assert ics.startswith("BEGIN:VCALENDAR\r\n")
        assert "END:VCALENDAR\r\n" in ics
        assert "BEGIN:VEVENT\r\n" in ics
        assert "END:VEVENT\r\n" in ics
        assert "VERSION:2.0\r\n" in ics

    def test_summary(self):
        start = datetime(2026, 3, 8, 14, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        end = datetime(2026, 3, 8, 15, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        ics = build_ics(start, end, "Meeting (Tokyo)", "Asia/Tokyo")

        assert "SUMMARY:Meeting (Tokyo)\r\n" in ics

    def test_times_in_utc(self):
        # Asia/Tokyo is UTC+9, so 14:30 JST = 05:30 UTC
        start = datetime(2026, 3, 8, 14, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        end = datetime(2026, 3, 8, 15, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        ics = build_ics(start, end, "Meeting", "Asia/Tokyo")

        assert "DTSTART:20260308T053000Z\r\n" in ics
        assert "DTEND:20260308T060000Z\r\n" in ics

    def test_has_uid(self):
        start = datetime(2026, 3, 8, 10, 0, tzinfo=ZoneInfo("UTC"))
        end = datetime(2026, 3, 8, 10, 30, tzinfo=ZoneInfo("UTC"))
        ics = build_ics(start, end, "Meeting", "UTC")

        assert "UID:" in ics

    def test_has_dtstamp(self):
        start = datetime(2026, 3, 8, 10, 0, tzinfo=ZoneInfo("UTC"))
        end = datetime(2026, 3, 8, 10, 30, tzinfo=ZoneInfo("UTC"))
        ics = build_ics(start, end, "Meeting", "UTC")

        assert "DTSTAMP:" in ics

    def test_crlf_line_endings(self):
        start = datetime(2026, 3, 8, 10, 0, tzinfo=ZoneInfo("UTC"))
        end = datetime(2026, 3, 8, 10, 30, tzinfo=ZoneInfo("UTC"))
        ics = build_ics(start, end, "Meeting", "UTC")

        # Every line should end with \r\n
        lines = ics.split("\r\n")
        # Last element after final \r\n is empty string
        assert lines[-1] == ""
        # No bare \n without \r
        assert "\n" not in ics.replace("\r\n", "")
