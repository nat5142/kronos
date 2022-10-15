import os
import pytz
from typing import Union
from datetime import tzinfo


def get_default_daterange():
    env_var_value = os.environ.get('KRONOS_DATERANGE', 'LATEST')
    if env_var_value in _VALID_DATERANGE_NAMES:
        return env_var_value
    elif env_var_value.lower() in [x.lower() for x in _VALID_DATERANGE_NAMES]:
        return env_var_value
    else:
        raise ValueError('Environment variable `KRONOS_DATERANGE` invalid or not set. Accepted values: {}'.format(_VALID_DATERANGE_NAMES))


def _get_valid_relative_ranges():
    return ['LAST_WEEK__{}'.format(abbr) for abbr in ['SUN', 'MON', 'TUES', 'WED', 'THURS', 'FRI', 'SAT', 'SUN']]


_VALID_DATERANGE_NAMES = [
    'LATEST',
    'YESTERDAY_TODAY',
    'LAST_MONTH,'
    'LAST_7_DAYS',
    'LAST_30_DAYS',
    *_get_valid_relative_ranges()
]


def make_timezone(timezone: Union[pytz.timezone, str]) -> pytz.timezone:
    """ Handle timezones given both as strings or as pre-made pytz.timezone objects.

    :param tz: a timezone, represented as a string or as as a pytz.timezone object.
    :type tz: _type_
    """
    if isinstance(timezone, tzinfo):
        # check if user already created the timezone object instead of passing a string, and handle it
        tz = timezone
    else:
        # accept string
        tz = pytz.timezone(timezone)

    return tz
