import data


class TestFlags:
    def test_flags_not_empty(self):
        assert len(data.flags) > 0

    def test_common_timezones_present(self):
        assert "America/New_York" in data.flags
        assert "Europe/London" in data.flags
        assert "Asia/Tokyo" in data.flags

    def test_values_are_emoji(self):
        for tz, flag in data.flags.items():
            assert len(flag) > 0, f"empty flag for {tz}"

    def test_us_flag(self):
        assert data.flags["America/New_York"] == "🇺🇸"

    def test_missing_timezone_not_present(self):
        assert "Fake/Timezone" not in data.flags
