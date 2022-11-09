import os
import pytz
import pytest
import typing
from datetime import datetime, timedelta

from src.kronos.kronos import Kronos, DEFAULT_TZ, DEFAULT_FORMAT, ISO_FMT

tz = pytz.timezone(DEFAULT_TZ)


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


def test_mtd_environment_variable():
    os.environ['KRONOS_DATERANGE'] = 'MTD'
    from src.kronos.kronos import Kronos
    kronos = Kronos()
    assert kronos._start_date.day == 1
    assert datetime.now().strftime(kronos.date_format) == kronos.end_date


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
