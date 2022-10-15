""" Main module. """
from __future__ import annotations

import os
from time import time
import pytz
from typing import Union, List
from dateutil.rrule import rrule, DAILY
from datetime import datetime, timedelta, tzinfo
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA

from src.kronos.utilities import get_default_daterange, make_timezone


ISO_FMT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TZ = os.environ.get('KRONOS_TIMEZONE', 'UTC')  # Defaults to EST if not set
DEFAULT_FORMAT = os.environ.get('KRONOS_FORMAT', '%Y-%m-%d')

REL_RANGE_MAP = {
    'SUN': SU,
    'MON': MO,
    'TUES': TU,
    'WED': WE,
    'THURS': TH,
    'FRI': FR,
    'SAT': SA
}


class Kronos(object):

    def __init__(self, start_date: str = None, end_date: str = None, timezone: Union[tzinfo, str] = DEFAULT_TZ,
                 date_format: str = DEFAULT_FORMAT):
        """ Generate a Kronos date range given a start date and end date (given as strings). Optionally
        provide a timezone (defaults to UTC).

        :param start_date: date range start date, in format defined by `date_format`. defaults to yesterday.
        :type start_date: str
        :param end_date: date range end date, in format defined by `date_format`, defaults to today.
        :type end_date: str
        :param timezone: (optional) timezone. defaults to environment var `KRONOS_TIMEZONE`, "UTC" if not set.
        :type timezone: Union[tzinfo, str] (optional) either a pre-built timzeone or a valid pytz timezone name.
        :param date_format: (optional) strftime format string that will be used as default format for your object. Read by `KRONOS_FORMAT` environment variable. Defaults to YYYY-MM-DD.
        :type date_format: str
        """

        self.tz = make_timezone(timezone=timezone)

        self.date_format = date_format

        if end_date:
            ed = datetime.strptime(end_date, date_format)
        else:
            # default to today
            ed = datetime.now()

        if start_date:
            sd = datetime.strptime(start_date, date_format)
        else:
            default_daterange = get_default_daterange()
            # TODO: implement additonal default daterange options
            if default_daterange in ['LATEST', 'YESTERDAY_TODAY']:
                sd = datetime.now() - timedelta(days=1)
            elif default_daterange.startswith('LAST_WEEK__'):
                day_abbr = default_daterange.split('__')[-1]  # get start day from value
                sd = datetime.now() - relativedelta(weekday=REL_RANGE_MAP[day_abbr](-1))
        
        if sd > ed:
            raise ValueError('`start_date` cannot come after `end_date`.')
        
        # set time to beginning/end of day
        self._start_date: datetime = self.tz.localize(sd.replace(hour=0, minute=0, second=0, microsecond=0))
        self._end_date: datetime = self.tz.localize(ed.replace(hour=23, minute=59, second=59, microsecond=999999))

    @property
    def start_date(self) -> str:
        return self._start_date.strftime(self.date_format)

    @property
    def end_date(self) -> str:
        return self._end_date.strftime(self.date_format)

    @property
    def current_date(self) -> datetime:
        """ Return the current local date as a datetime object. """
        return datetime.now(tz=self.tz)

    @property
    def today(self) -> str:
        return self.current_date.strftime(self.date_format)

    @property
    def yesterday(self):
        return (self.current_date - timedelta(days=1)).strftime(self.date_format)

    @staticmethod
    def convert_date(dt_str, in_format, out_format) -> str:
        """ Convert a date in format `in_format` and return string in format `out_format`. """
        parsed_date = datetime.strptime(dt_str, in_format)
        return parsed_date.strftime(out_format)

    @staticmethod
    def from_timestamp(unix_timestamp) -> str:
        """ Convenience pass-thru to datetime.fromtimestamp(...). Returns YYYY-MM-DD formatted date. """
        return datetime.fromtimestamp(unix_timestamp)

    def day_range(self) -> List[Kronos]:
        """ Return a list of one-day Kronos objects for each date between objects' start and end date. """
        for day in rrule(DAILY, dtstart=self._start_date, until=self._end_date):
            yield Kronos(day.strftime(self.date_format), day.strftime(self.date_format), date_format=self.date_format, timezone=self.tz)

    def now(self, timezone: Union[pytz.timezone, str]=None) -> datetime:
        """ Convenience func to return current local time specified by `timezone`. 
        
        :param timezone: (optional) timezone. returned as `self.tz` if not provided.
        :return: datetime object
        """
        if timezone:
            tz = make_timezone(timezone=timezone)
        else:
            tz = self.tz

        return datetime.now(tz=tz)

    @classmethod
    def last_x_days(cls, x: int = 30) -> Kronos:
        """Get the last `x` days since today.

        :param x: number of days to go back, defaults to 30
        :type x: int, optional
        """
        start_date = cls.now() - timedelta(days=x)
        return Kronos(start_date=start_date.strftime('%Y-%m-%d'), end_date=cls.now().strftime('%Y-%m-%d'))
    
    def list_date_range(self) -> List[datetime]:
        """ List all dates in the Kronos daterange as datetime objects.

        :return: a list of each day in the range
        :rtype: List[datetime]
        """
        return list(rrule(freq=DAILY, dtstart=self._start_date, until=self._end_date))

    def format_start(self, out_format) -> str:
        """ Return start date in specified format.

        :param out_format: a valid strftime format
        :return: start date string in out_format
        """
        return self._start_date.strftime(out_format)

    def format_end(self, out_format) -> str:
        """ Return end date in specified format.

        :param out_format: a valid strftime format
        :return: end date string in out_format
        """
        return self._end_date.strftime(out_format)

    def shift_start_tz(self, target_tz='UTC') -> datetime:
        """ Shift the start_date timezone from self.tz to a timezone specified by `target_tz`

        :param target_tz: offer target timezone, defaults to 'UTC'
        :type target_tz: str, optional
        :return: timezone-aware datetime object
        """
        return self._start_date.astimezone(tz=pytz.timezone(target_tz))

    def shift_end_tz(self, target_tz='UTC') -> datetime:
        """ Shift the end_date timezone from self.tz to a timezone specified by `target_tz`

        :param target_tz: offer target timezone, defaults to 'UTC'
        :type target_tz: str, optional
        :return: timezone-aware datetime object
        """
        return self._end_date.astimezone(tz=pytz.timezone(target_tz))

    def __repr__(self):
        return "Kronos(start_date='{}', end_date='{}', date_format='{}', timezone='{}')".format(
            self.start_date, self.end_date, self.date_format, self.tz.zone
        )

