import os
import pytz
import pytest
import typing
from datetime import datetime, timedelta
from kronos.utilities import make_timezone

from src.kronos.kronos import Kronos, DEFAULT_TZ, DEFAULT_FORMAT, ISO_FMT

tz = pytz.timezone(DEFAULT_TZ)

os.environ['KRONOS_DATERANGE'] = 'LATEST'


def test_no_start_date():
    with pytest.raises(AttributeError):
        today = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
        kronos = Kronos(start_date=None, end_date=today)


def test_no_end_date():
    yesterday = (datetime.now(tz=tz) - timedelta(days=1)).strftime(DEFAULT_FORMAT)
    today = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
    kronos = Kronos(start_date=yesterday, end_date=None)

    assert kronos.start_date == yesterday
    assert kronos.end_date == today
    # use fget to reference properties
    assert type(kronos.start_date) == typing.get_type_hints(Kronos.start_date.fget).get('return')
    assert type(kronos.end_date) == typing.get_type_hints(Kronos.end_date.fget).get('return')


def test_no_dates_input():
    today = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
    yesterday = (datetime.now(tz=tz) - timedelta(days=1)).strftime(DEFAULT_FORMAT)
    kronos = Kronos()

    assert kronos.start_date == yesterday
    assert kronos.end_date == today


def test_datetime_inputs():
    today = datetime.now(tz=tz).strftime(ISO_FMT)
    yesterday = (datetime.now(tz=tz) - timedelta(days=1)).strftime(ISO_FMT)

    kronos = Kronos(yesterday, today, date_format=ISO_FMT)

    assert kronos.start_date == yesterday
    assert kronos.end_date == today


def test_last_month_env_variable():
    os.environ['KRONOS_DATERANGE'] = 'LAST_MONTH'
    from src.kronos.kronos import Kronos
    kronos = Kronos()
    assert kronos._start_date.day == 1
    assert (kronos._end_date + timedelta(days=1)).day == 1
    os.environ['KRONOS_DATERANGE'] = 'LATEST'


def test_mtd_environment_variable():
    os.environ['KRONOS_DATERANGE'] = 'MTD'
    from src.kronos.kronos import Kronos
    kronos = Kronos()
    assert kronos._start_date.day == 1
    assert datetime.now().strftime(kronos.date_format) == kronos.end_date
    os.environ['KRONOS_DATERANGE'] = 'LATEST'


def test_manual_entry_named_ranges():
    today = datetime.now(tz=tz).strftime('%Y-%m-%d')
    kronos = Kronos(named_range='TODAY')
    assert kronos.start_date == today
    assert kronos.end_date == today
    kronos = Kronos(named_range='MTD')
    assert kronos._start_date.day == 1
    assert datetime.now().strftime(kronos.date_format) == kronos.end_date
    kronos = Kronos(named_range='LAST_MONTH')
    assert kronos._start_date.day == 1
    assert (kronos._end_date + timedelta(days=1)).day == 1


def test_datetime_obj_start_date():
    start_dt = datetime(2023, 3, 1, 12, 59, 59)
    kronos = Kronos(start_dt)
    assert kronos.format_start(ISO_FMT) == '2023-03-01 12:59:59'


def test_datetime_obj_end_date():
    end_dt = datetime(2023, 3, 8, 23, 59, 59)
    kronos = Kronos('2023-03-01', end_dt)
    assert kronos.format_end(ISO_FMT) == '2023-03-08 23:59:59'


def test_init_with_datetime_aware_start_date():
    timezone = make_timezone(DEFAULT_TZ)
    start_dt = timezone.localize(datetime(2023, 3, 7, 0, 0, 0))
    kronos = Kronos(start_dt, '2023-03-08')
    assert kronos.timezone == DEFAULT_TZ
    assert kronos.format_start(ISO_FMT) == '2023-03-07 00:00:00'


def test_init_with_datetime_unaware_start_date():
    start_dt = datetime(2023, 3, 7, 0, 0, 0)
    kronos = Kronos(start_dt, '2023-03-08')  # should fall back to `KRONOS_DATERANGE` environment variable
    assert kronos.timezone == DEFAULT_TZ
    assert kronos.format_start(ISO_FMT) == '2023-03-07 00:00:00'


def test_init_with_datetime_aware_end_date():
    timezone = make_timezone(DEFAULT_TZ)
    end_dt = timezone.localize(datetime(2023, 3, 8, 23, 59, 59))
    kronos = Kronos('2023-03-07', end_dt)
    assert kronos.timezone == DEFAULT_TZ
    assert kronos.format_end(ISO_FMT) == '2023-03-08 23:59:59'


def test_init_with_datetime_unaware_end_date():
    end_dt = datetime(2023, 3, 9, 23, 59, 59)
    kronos = Kronos('2023-03-01', end_dt)  # should fall back to `KRONOS_DATERANGE` environment variable
    assert kronos.timezone == DEFAULT_TZ
    assert kronos.format_end(ISO_FMT) == '2023-03-09 23:59:59'


def test_datetime_aware_start_and_end_dates_same_timezone():
    timezone = make_timezone(DEFAULT_TZ)
    start_dt = datetime(2023, 3, 1)
    end_dt = datetime(2023, 3, 9)
    # check for same timezone
    kronos = Kronos(timezone.localize(start_dt), timezone.localize(end_dt))
    assert kronos.timezone == DEFAULT_TZ
    assert kronos.format_start(ISO_FMT) == '2023-03-01 00:00:00'
    assert kronos.format_end(ISO_FMT) == '2023-03-09 23:59:59'


def test_datetime_aware_start_and_end_dates_different_timezones():
    start_dt = make_timezone('UTC').localize(datetime(2023, 3, 1, 8, 0, 0))
    end_dt = make_timezone('America/Los_Angeles').localize(datetime(2023, 3, 9, 0, 0, 0))
    kronos = Kronos(start_dt, end_dt, timezone=DEFAULT_TZ)
    assert kronos.timezone == DEFAULT_TZ
    assert kronos.format_start(ISO_FMT) == '2023-03-01 03:00:00'
    assert kronos.format_end(ISO_FMT) == '2023-03-09 03:00:00'
    assert kronos.shift_start_tz(target_tz='UTC').strftime(ISO_FMT) == start_dt.strftime(ISO_FMT)
    assert kronos.shift_end_tz(target_tz='America/Los_Angeles').strftime(ISO_FMT) == end_dt.strftime(ISO_FMT)


def test_init_with_datetime_unaware_start_and_end_dates():
    start_dt = datetime(2023, 3, 1)
    end_dt = datetime(2023, 3, 9)
    kronos = Kronos(start_dt, end_dt, timezone=DEFAULT_TZ)
    assert kronos.timezone == DEFAULT_TZ
