"""Tests for `kronos` module."""
import typing

import pytest

import os
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
    assert version == "0.0.8"


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
