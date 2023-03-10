import os
import re
import pytz
from typing import Union, Tuple
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA

REL_RANGE_MAP = {
    'SUN': SU,
    'MON': MO,
    'TUES': TU,
    'WED': WE,
    'THURS': TH,
    'FRI': FR,
    'SAT': SA
}

_VALID_RELATIVE_DAY_ABBRS = ['SUN', 'MON', 'TUES', 'WED', 'THURS', 'FRI', 'SAT']



def get_default_daterange(tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get the default (fallback) timezone used by Kronos.

    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :raises ValueError: if an invalid `KRONOS_DATERANGE` is specified.
    :return: (start_dt, end_dt) for Kronos initialization.
    :rtype: Tuple[datetime, datetime]
    """
    end_dt = None
    start_dt = None
    env_var_value = os.environ.get('KRONOS_DATERANGE', 'LATEST')

    start_dt, end_dt = _get_named_daterange(env_var_value, tz)
    
    if start_dt is None and end_dt is None:
        raise ValueError(f'Environment variable `KRONOS_DATERANGE` invalid (value: {env_var_value}). See docs for accepted values.')
    
    return start_dt, end_dt


def _get_named_daterange(range_name: str, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get a valid named daterange.

    :param range_name: a valid daterange name (all valid values for `KRONOS_DATERANGE`) 
    :type range_name: str
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: (start_dt, end_dt)
    :rtype: Tuple[datetime, datetime]
    """
    start_dt = end_dt = None
    for regex, func in _VALID_DATERANGES.items():
        match = re.match(regex, range_name)
        if match:
            start_dt, end_dt = func(match, tz)
            break
    
    return start_dt, end_dt


def make_timezone(timezone: Union[pytz.BaseTzInfo, str]) -> pytz.BaseTzInfo:
    """ Handle timezones given both as strings or as pre-made pytz.BaseTzInfo objects.

    :param tz: a timezone, represented as a string or as as a pytz.timezone object.
    """
    if isinstance(timezone, pytz.BaseTzInfo):
        # check if user already created the timezone object instead of passing a string, and handle it
        tz = timezone
    else:
        # accept string
        tz = pytz.timezone(timezone)

    return tz


def convert_timezone(date_obj: datetime, in_tz: Union[pytz.BaseTzInfo, str], out_tz: Union[pytz.BaseTzInfo, str]) -> datetime:
    """ Convert a date object from one timezone to another (changes time components --> see `change_timezone` if you want to)

    :param date_obj: a datetime object to convert
    :type date_obj: datetime
    :param in_tz: timezone to convert from
    :type in_tz: Union[pytz.BaseTzInfo, str]
    :param out_tz: timezone to convert to
    :type out_tz: Union[pytz.BaseTzInfo, str]
    :rtype: datetime
    """
    if date_obj.tzinfo is None:
        in_timezone = make_timezone(in_tz)
        date_obj = in_timezone.localize(date_obj)
    out_timezone = make_timezone(out_tz)
    return date_obj.astimezone(tz=out_timezone)


def latest(match: re.Match, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get default daterange of (yesterday, today)

    :param match: regex Match object
    :type match: re.Match
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: (yesterday, today) as YYYY-MM-DD date strings
    :rtype: Tuple[datetime, datetime]
    """
    timezone = make_timezone(tz)
    now = datetime.now(tz=timezone)
    return (now - relativedelta(days=1)), (now)

def today(match: re.Match, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get just "today" a range.

    :param match: regex Match object
    :type match: re.Match
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: (today, today) as YYYY-MM-DD date strings
    :rtype: Tuple[datetime, datetime]
    """
    timezone = make_timezone(tz)
    now = datetime.now(tz=timezone)
    return (now, now)

def last_month(match: re.Match, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get daterange containing last month

    :param match: regex Match object
    :type match: re.Match
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: last month (start, end) as YYYY-MM-DD date strings
    :rtype: Tuple[datetime, datetime]
    """
    timezone = make_timezone(tz)
    now = datetime.now(tz=timezone).replace(day=1)  # first day of this month
    end_dt = now.replace(day=1) - timedelta(days=1)  # last day of last month
    start_dt = end_dt.replace(day=1)
    return start_dt, end_dt


def month_to_date(match: re.Match, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get daterange for MTD.

    :param match: regex Match object
    :type match: re.Match
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: MTD (1st, today) as YYYY-MM-DD date strings
    :rtype: Tuple[datetime, datetime]
    """
    timezone = make_timezone(tz)
    now = datetime.now(tz=timezone)
    start_dt = now.replace(day=1)
    return start_dt, now


def last_x_days(match: re.Match, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get date boundaries for `x` days ago until today

    :param match: regex Match object
    :type match: re.Match
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: (x days ago, today) as YYYY-MM-DD date strings
    :rtype: Tuple[datetime, datetime]
    """
    match_group = match.groupdict()
    timezone = make_timezone(tz)
    now = datetime.now(tz=timezone)
    start_dt = now - timedelta(days=int(match_group['var']))
    return start_dt, now


def week_to_date_starting_on(match: re.Match, tz: Union[pytz.BaseTzInfo, str]) -> Tuple[datetime, datetime]:
    """ Get date boundaries for the last `weekday` until today. 

    :param match: regex Match object
    :type match: re.Match
    :param tz: either a pre-built timzeone or a valid pytz timezone name
    :type tz: Union[pytz.BaseTzInfo, str]
    :return: (last `weekday`, today) as YYYY-MM-DD date strings
    :rtype: Tuple[datetime, datetime]
    """
    weekday = match.groupdict()['var']
    if weekday.upper() not in _VALID_RELATIVE_DAY_ABBRS:
        raise ValueError(f'Weekday abbreviation "{weekday}" is not accepted. Check your `KRONOS_DATERANGE` environment variable. Accepted values: {_VALID_RELATIVE_DAY_ABBRS}')
    
    timezone = make_timezone(tz)
    now = datetime.now(tz=timezone)
    start_dt = now - relativedelta(weekday=REL_RANGE_MAP[weekday](-1))
    return start_dt, now


def handle_ambiguous_datetime(datetime_item: Union[datetime, str], timezone: Union[pytz.BaseTzInfo, str], fmt: str = '%Y-%m-%d') -> datetime:
    """ Accept datetimes as strings, datetime objects, or date objects. Return the value as a localized datetime object.

    :param datetime_item: a datetime as a string or datetime object
    :type datetime_item: Union[datetime, str]
    :param timezone: the timezone we will convert `datetime_item` into
    :type timezone: Union[pytz.BaseTzInfo, str], either a pre-built timzeone or a valid pytz timezone name
    :param fmt: if a string is provided for `datetime_item`, provide a datetime strftime string here. defaults to `%Y-%m-%d`
    :type fmt: str
    :return: a localized datetime object
    :rtype: datetime
    """
    tz = make_timezone(timezone)
    if isinstance(datetime_item, datetime):
        if datetime_item.tzinfo is None:
            ret = tz.localize(datetime_item)
        else:
            ret = convert_timezone(date_obj=datetime_item, in_tz=datetime_item.tzinfo, out_tz=tz)
    elif isinstance(datetime_item, str):
        ret = tz.localize(datetime.strptime(datetime_item, fmt))
    
    return ret



_VALID_DATERANGES = {
    r'^LATEST$': latest,
    r'^YESTERDAY_TODAY$': latest,
    r'^TODAY$': today,
    r'^LAST_MONTH$': last_month,
    r'^MTD$': month_to_date,
    r'^LAST_(?P<var>\d+)_DAYS$': last_x_days,
    r'^THIS_WEEK__(?P<var>\w+)$': week_to_date_starting_on
}
