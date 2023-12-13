"""Tests for `kronos` module."""
import os
import typing
import pytest

from kronos.utilities import make_timezone
os.environ['KRONOS_DATERANGE'] = 'LATEST'

import pytz
from datetime import datetime, timedelta

import src.kronos as k
from src.kronos.kronos import ISO_FMT, Kronos, DEFAULT_TZ, DEFAULT_FORMAT

tz = pytz.timezone(DEFAULT_TZ)

class ParentKronos(Kronos):
    def this_function_should_exist(self):
        pass


@pytest.fixture
def version() -> typing.Generator[str, None, None]:
    """Sample pytest fixture."""
    yield k.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.0.14"


def test_day_range():
    end_date = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
    start_date = (datetime.now(tz=tz) - timedelta(days=5)).strftime(DEFAULT_FORMAT)

    kronos = Kronos(start_date, end_date)

    day_range = [x for x in kronos.day_range()]

    assert len(day_range) == 6


def test_set_start_time():
    kronos = Kronos()
    kronos.set_start_time(hour=8, minute=30, second=15)

    assert kronos.format_start('%H:%M:%S') == '08:30:15'

def test_set_end_time():
    kronos = Kronos()
    kronos.set_end_time(hour=8, minute=30, second=15)

    assert kronos.format_end('%H:%M:%S') == '08:30:15'

def test_start_timestamp():
    kronos = Kronos()
    # use fget to reference properties
    assert type(kronos.start_ts) == typing.get_type_hints(Kronos.start_ts.fget).get('return')

def test_end_timestamp():
    kronos = Kronos()
    assert type(kronos.end_ts) == typing.get_type_hints(Kronos.end_ts.fget).get('return')


def test_set_start_time():
    kronos = Kronos()
    kronos.set_start_time(hour=12, minute=15, second=59)
    assert kronos.format_start(ISO_FMT).split(' ')[-1] == '12:15:59'


def test_set_end_time():
    kronos = Kronos()
    kronos.set_end_time(hour=12, minute=15, second=59)
    assert kronos.format_end(ISO_FMT).split(' ')[-1] == '12:15:59'


def test_last_x_days():
    kronos = Kronos().last_x_days(30)
    assert type(kronos) == Kronos


def test_override_class_retention():
    kronos = ParentKronos()
    last_x_days_kronos = kronos.last_x_days(30)
    assert hasattr(last_x_days_kronos, 'this_function_should_exist')
    
    shift_range_kronos = kronos.shift_range(days=-5)
    assert hasattr(shift_range_kronos, 'this_function_should_exist')

    day_range_kronos_list = last_x_days_kronos.day_range()
    assert all([hasattr(x, 'this_function_should_exist') for x in day_range_kronos_list])


def test_splice_kronos_with_string():
    kronos = Kronos('2023-03-01', '2023-03-08')
    dt = '2023-03-05 12:00:01'
    k1, k2 = kronos.splice(dt, fmt=ISO_FMT)
    assert k1.format_end(ISO_FMT) == dt
    assert k2.format_start(ISO_FMT) == dt

    dt = '2023-03-05T12:00:01.123Z'
    k1, k2 = kronos.splice(dt, fmt='%Y-%m-%dT%H:%M:%S.%fZ')
    assert k1.format_end(ISO_FMT) == '2023-03-05 12:00:01'
    assert k2.format_start(ISO_FMT) == '2023-03-05 12:00:01'


def test_splice_kronos_with_datetime():
    timezone = make_timezone('UTC')
    kronos = Kronos('2023-03-01', '2023-03-08', timezone='UTC')
    dt = timezone.localize(datetime(2023, 3, 5, 12, 0, 1))
    k1, k2 = kronos.splice(dt)
    assert k1.format_end(ISO_FMT) == '2023-03-05 12:00:01'
    assert k2.format_start(ISO_FMT) == '2023-03-05 12:00:01'


# recall that Kronos(start_date=None, end_date=...) is invalid
def test_beginning_and_end_of_day_for_omitted_start_date():
    with pytest.raises(AttributeError):
        today = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
        kronos = Kronos(start_date=None, end_date=today)


def test_beginning_and_end_of_day_for_omitted_end_date():
    yesterday = (datetime.now(tz=tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now(tz=tz).strftime('%Y-%m-%d')
    kronos = Kronos(start_date=yesterday, end_date=None)

    assert kronos.start_date == yesterday
    assert kronos.end_date == today

    assert kronos._start_date.hour == 0
    assert kronos._start_date.minute == 0
    assert kronos._start_date.second == 0
    assert kronos._start_date.microsecond == 0

    assert kronos._end_date.hour == 23
    assert kronos._end_date.minute == 59
    assert kronos._end_date.second == 59
    assert kronos._end_date.microsecond == 999999


def  test_beginning_and_end_of_day_for_omitted_both():
    yesterday = (datetime.now(tz=tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now(tz=tz).strftime('%Y-%m-%d')
    kronos = Kronos(start_date=None, end_date=None)

    assert kronos.start_date == yesterday
    assert kronos.end_date == today

    assert kronos._start_date.hour == 0
    assert kronos._start_date.minute == 0
    assert kronos._start_date.second == 0
    assert kronos._start_date.microsecond == 0

    assert kronos._end_date.hour == 23
    assert kronos._end_date.minute == 59
    assert kronos._end_date.second == 59
    assert kronos._end_date.microsecond == 999999


def test_from_timestamp():
    timezone = 'America/New_York'
    sample_unix_timestamp = 1702505330
    dt = Kronos(date_format='%Y-%m-%d').from_timestamp(sample_unix_timestamp)
    assert dt.strftime('%Y-%m-%d') == '2023-12-13'

    dt_local = Kronos(date_format='%Y-%m-%d').from_timestamp(sample_unix_timestamp, in_timezone=timezone)
    assert dt_local.tzinfo.zone == timezone
    assert dt_local.hour == 17

    dt_local_to_utc = Kronos(date_format='%Y-%m-%d').from_timestamp(sample_unix_timestamp, in_timezone='America/New_York', out_timezone='UTC')
    assert dt_local_to_utc.tzinfo.zone == 'UTC'
    assert dt_local_to_utc.hour == 22
