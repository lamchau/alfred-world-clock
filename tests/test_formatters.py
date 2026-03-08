from datetime import datetime, timezone

import pytest

import formatters


@pytest.fixture
def now():
    return datetime(2026, 3, 8, 14, 30, 45, 123456, tzinfo=timezone.utc)


class TestDefault24hs:
    def test_format(self, now):
        assert formatters.default_24hs(now) == "14:30:45 (March 08, 2026)"


class TestDefault12hs:
    def test_format_is_lowercase(self, now):
        result = formatters.default_12hs(now)
        assert result == result.lower()

    def test_format(self, now):
        assert formatters.default_12hs(now) == "02:30:45 pm (march 08, 2026)"


class TestIso8601:
    def test_includes_microseconds(self, now):
        result = formatters.iso8601(now)
        assert ".123456" in result

    def test_format(self, now):
        result = formatters.iso8601(now)
        assert result.startswith("2026-03-08T")


class TestIso8601WithoutMicroseconds:
    def test_no_microseconds(self, now):
        result = formatters.iso8601_without_microseconds(now)
        assert ".123456" not in result

    def test_format(self, now):
        result = formatters.iso8601_without_microseconds(now)
        assert result.startswith("2026-03-08T")


class TestCustom:
    def test_custom_format(self, now):
        fmt = formatters.custom("%H:%M")
        assert fmt(now) == "14:30"

    def test_custom_ampm(self, now):
        fmt = formatters.custom("%I:%M %p")
        assert fmt(now) == "02:30 PM"

    def test_returns_callable(self):
        fmt = formatters.custom("%H:%M")
        assert callable(fmt)


class TestFormattersDict:
    def test_default_is_24hs(self):
        assert formatters.FORMATTERS["FORMAT_DEFAULT"] is formatters.default_24hs

    def test_all_keys_present(self):
        expected = {
            "FORMAT_DEFAULT",
            "FORMAT_DEFAULT_12HS",
            "FORMAT_DEFAULT_24HS",
            "FORMAT_ISO8601_WITH_MICROSECONDS",
            "FORMAT_ISO8601_WITHOUT_MICROSECONDS",
        }
        assert set(formatters.FORMATTERS.keys()) == expected

    def test_all_values_callable(self):
        for key, fn in formatters.FORMATTERS.items():
            assert callable(fn), f"{key} is not callable"
