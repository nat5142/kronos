import pytz

from src.kronos.utilities import make_timezone


def test_make_timezone_with_str():
    tz = 'America/New_York'
    timezone = make_timezone(tz)

    assert isinstance(timezone, pytz.BaseTzInfo)


def test_make_timezone_with_premade_arg():
    tz = pytz.timezone('America/New_York')
    timezone = make_timezone(tz)

    assert isinstance(timezone, pytz.BaseTzInfo)

