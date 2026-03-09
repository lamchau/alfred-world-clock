from datetime import datetime, timedelta, timezone

import pytest

from main import convert_to_time, convert_to_date, convert_to_delta, timeparse, is_duration, has_calendar_units, gdate_parse, expand_units


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


class TestExpandUnits:
    def test_short_hours(self):
        assert expand_units("3h") == "3 hours"

    def test_short_minutes(self):
        assert expand_units("22m") == "22 minutes"

    def test_short_seconds(self):
        assert expand_units("90s") == "90 seconds"

    def test_mixed(self):
        assert expand_units("2 days 3h 22m") == "2 days 3 hours 22 minutes"

    def test_short_days(self):
        assert expand_units("3d") == "3 days"

    def test_short_weeks(self):
        assert expand_units("2w") == "2 weeks"

    def test_already_long(self):
        assert expand_units("3 hours 22 minutes") == "3 hours 22 minutes"

    def test_combined_no_spaces(self):
        assert expand_units("2days3h22m") == "2 days3 hours22 minutes"

    def test_hr_form(self):
        assert expand_units("3hr") == "3 hours"

    def test_min_form(self):
        assert expand_units("30min") == "30 minutes"

    def test_sec_form(self):
        assert expand_units("90sec") == "90 seconds"


class TestHasCalendarUnits:
    def test_days(self):
        assert has_calendar_units("3 days") is True
        assert has_calendar_units("1day") is True
        assert has_calendar_units("3d") is True

    def test_weeks(self):
        assert has_calendar_units("2 weeks") is True
        assert has_calendar_units("1week") is True
        assert has_calendar_units("2w") is True

    def test_months(self):
        assert has_calendar_units("3 months") is True
        assert has_calendar_units("1month") is True

    def test_years(self):
        assert has_calendar_units("1 year") is True
        assert has_calendar_units("2years") is True

    def test_combined(self):
        assert has_calendar_units("3 months 2 days") is True

    def test_no_calendar_units(self):
        assert has_calendar_units("3h") is False
        assert has_calendar_units("30m") is False
        assert has_calendar_units("1h30m") is False


class TestGdateParse:
    def test_months(self):
        result = gdate_parse("3 months")
        now = datetime.now(timezone.utc)
        # should be roughly 3 months from now
        diff = result - now
        assert 80 < diff.days < 100

    def test_weeks(self):
        result = gdate_parse("2 weeks")
        now = datetime.now(timezone.utc)
        diff = result - now
        assert 13 <= diff.days <= 15

    def test_days(self):
        result = gdate_parse("5 days")
        now = datetime.now(timezone.utc)
        diff = result - now
        assert 4 <= diff.days <= 6

    def test_negative(self):
        result = gdate_parse("-3 months")
        now = datetime.now(timezone.utc)
        diff = now - result
        assert 80 < diff.days < 100

    def test_combined(self):
        result = gdate_parse("3 months 3 days")
        now = datetime.now(timezone.utc)
        diff = result - now
        assert 83 < diff.days < 103

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="gdate could not parse"):
            gdate_parse("not_a_valid_expression_xyz")


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
