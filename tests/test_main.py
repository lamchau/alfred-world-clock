from datetime import timedelta

import pytest

from main import convert_to_time, convert_to_date, convert_to_delta, timeparse, is_duration


class TestConvertToTime:
    def test_hh_mm_ss(self):
        assert convert_to_time("14:30:45") == (14, 30, 45)

    def test_hh_mm(self):
        assert convert_to_time("14:30") == (14, 30, 0)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="should follow the formats"):
            convert_to_time("invalid")

    def test_midnight(self):
        assert convert_to_time("00:00") == (0, 0, 0)

    def test_5pm(self):
        assert convert_to_time("5pm") == (17, 0, 0)

    def test_5am(self):
        assert convert_to_time("5am") == (5, 0, 0)

    def test_12pm(self):
        assert convert_to_time("12pm") == (12, 0, 0)

    def test_12am(self):
        assert convert_to_time("12am") == (0, 0, 0)

    def test_5_30pm(self):
        assert convert_to_time("5:30pm") == (17, 30, 0)

    def test_5_30am(self):
        assert convert_to_time("5:30am") == (5, 30, 0)

    def test_case_insensitive(self):
        assert convert_to_time("5PM") == (17, 0, 0)
        assert convert_to_time("5Pm") == (17, 0, 0)

    def test_with_space(self):
        assert convert_to_time("5 pm") == (17, 0, 0)
        assert convert_to_time("5:30 pm") == (17, 30, 0)


class TestConvertToDate:
    def test_dd_mm_yyyy(self):
        assert convert_to_date("08/03/2026") == (8, 3, 2026)

    def test_yyyy_mm_dd(self):
        assert convert_to_date("2026-03-08") == (8, 3, 2026)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="should follow the formats"):
            convert_to_date("invalid")


class TestTimeparse:
    def test_hours_short(self):
        assert timeparse("3h") == 3 * 3600

    def test_hours_long(self):
        assert timeparse("3hours") == 3 * 3600

    def test_hours_hr(self):
        assert timeparse("3hr") == 3 * 3600

    def test_hours_hrs(self):
        assert timeparse("3hrs") == 3 * 3600

    def test_decimal_hours(self):
        assert timeparse("3.5h") == 3.5 * 3600

    def test_decimal_hours_long(self):
        assert timeparse("1.5hours") == 1.5 * 3600

    def test_decimal_minutes(self):
        assert timeparse("1.5m") == 1.5 * 60

    def test_minutes_short(self):
        assert timeparse("30m") == 30 * 60

    def test_minutes_min(self):
        assert timeparse("30min") == 30 * 60

    def test_minutes_mins(self):
        assert timeparse("30mins") == 30 * 60

    def test_minutes_minute(self):
        assert timeparse("30minute") == 30 * 60

    def test_minutes_minutes(self):
        assert timeparse("30minutes") == 30 * 60

    def test_seconds_short(self):
        assert timeparse("90s") == 90

    def test_seconds_sec(self):
        assert timeparse("90sec") == 90

    def test_seconds_secs(self):
        assert timeparse("90secs") == 90

    def test_seconds_second(self):
        assert timeparse("90second") == 90

    def test_seconds_seconds(self):
        assert timeparse("90seconds") == 90

    def test_combined_hm(self):
        assert timeparse("1h30m") == 1 * 3600 + 30 * 60

    def test_combined_hms(self):
        assert timeparse("1h30m15s") == 1 * 3600 + 30 * 60 + 15

    def test_combined_with_spaces(self):
        assert timeparse("1h 30m") == 1 * 3600 + 30 * 60

    def test_colon_format(self):
        assert timeparse("3:30") == 3 * 3600 + 30 * 60

    def test_colon_format_single_digit(self):
        assert timeparse("1:00") == 1 * 3600

    def test_colon_format_with_sign(self):
        assert timeparse("+3:30") == 3 * 3600 + 30 * 60
        assert timeparse("-3:30") == 3 * 3600 + 30 * 60

    def test_strips_sign(self):
        assert timeparse("+3h") == 3 * 3600
        assert timeparse("-3h") == 3 * 3600

    def test_invalid_returns_none(self):
        assert timeparse("not_a_time") is None

    def test_empty_returns_none(self):
        assert timeparse("") is None

    def test_bare_number_returns_none(self):
        assert timeparse("123") is None


class TestIsDuration:
    def test_bare_duration(self):
        assert is_duration("3h") is True
        assert is_duration("30m") is True
        assert is_duration("90s") is True
        assert is_duration("1h30m") is True

    def test_decimal_duration(self):
        assert is_duration("3.5h") is True
        assert is_duration("1.5hours") is True

    def test_signed_duration(self):
        assert is_duration("+3h") is True
        assert is_duration("-1h30m") is True

    def test_long_form(self):
        assert is_duration("3hours") is True
        assert is_duration("30minutes") is True

    def test_colon_is_not_bare_duration(self):
        """bare 3:30 is ambiguous with clock time, so is_duration returns False.
        it only works as a duration with a sign prefix via convert_to_delta."""
        assert is_duration("3:30") is False
        assert is_duration("14:30") is False

    def test_not_duration(self):
        assert is_duration("hello") is False
        assert is_duration("123") is False


class TestConvertToDelta:
    def test_positive_offset(self):
        delta = convert_to_delta("1h30m")
        assert delta == timedelta(hours=1, minutes=30)

    def test_seconds(self):
        delta = convert_to_delta("90s")
        assert delta == timedelta(seconds=90)

    def test_hours_only(self):
        delta = convert_to_delta("2h")
        assert delta == timedelta(hours=2)

    def test_minutes_only(self):
        delta = convert_to_delta("45m")
        assert delta == timedelta(minutes=45)

    def test_negative_offset(self):
        delta = convert_to_delta("-2h")
        assert delta == timedelta(hours=-2)

    def test_negative_complex(self):
        delta = convert_to_delta("-1h30m")
        assert delta == timedelta(hours=-1, minutes=-30)

    def test_positive_sign(self):
        delta = convert_to_delta("+1h")
        assert delta == timedelta(hours=1)

    def test_decimal_hours(self):
        delta = convert_to_delta("3.5h")
        assert delta == timedelta(hours=3, minutes=30)

    def test_decimal_negative(self):
        delta = convert_to_delta("-1.5h")
        assert delta == timedelta(hours=-1, minutes=-30)

    def test_colon_signed(self):
        delta = convert_to_delta("+3:30")
        assert delta == timedelta(hours=3, minutes=30)

    def test_colon_negative(self):
        delta = convert_to_delta("-3:30")
        assert delta == timedelta(hours=-3, minutes=-30)

    def test_long_form(self):
        delta = convert_to_delta("2hours")
        assert delta == timedelta(hours=2)

    def test_long_form_minutes(self):
        delta = convert_to_delta("30minutes")
        assert delta == timedelta(minutes=30)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid time offset"):
            convert_to_delta("not_a_time")
