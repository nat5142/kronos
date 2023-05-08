""" Main module. """
from __future__ import annotations

import os
import warnings
from typing import Union, List, Generator, Tuple

import pytz
from dateutil.rrule import rrule, DAILY
from datetime import datetime, timedelta

from .utilities import get_default_daterange, make_timezone, convert_timezone, _get_named_daterange, handle_ambiguous_datetime

ISO_FMT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TZ = os.environ.get('KRONOS_TIMEZONE', 'UTC')  # Defaults to UTC if not set
DEFAULT_FORMAT = os.environ.get('KRONOS_FORMAT', '%Y-%m-%d')


class Kronos(object):

    def __init__(self, 
                start_date: Union[datetime, str] = None, 
                end_date: Union[datetime, str] = None, 
                timezone: Union[pytz.BaseTzInfo, str] = DEFAULT_TZ,
                date_format: str = DEFAULT_FORMAT,
                named_range: str = None):
        """ Generate a Kronos date range given a start date and end date (given as strings). Optionally
        provide a timezone (defaults to UTC). If you provide an `end_date`, you must also provide a 
        `start_date`. If `end_date` is omitted, it will default to today.

        :param start_date: date range start date, in format defined by `date_format`. defaults to yesterday.
        :type start_date: Union[datetime, str]
        :param end_date: date range end date, in format defined by `date_format`, defaults to today.
        :type end_date: Union[datetime, str]
        :param timezone: (optional) timezone. defaults to environment var `KRONOS_TIMEZONE`, "UTC" if not set.
        :type timezone: Union[pytz.BaseTzInfo, str] (optional) either a pre-built timzeone or a valid pytz timezone name.
        :param date_format: (optional) strftime format string that will be used as default format for your object. Read by `KRONOS_FORMAT` environment variable. Defaults to YYYY-MM-DD.
        :type date_format: str
        :param named_range: (optional) a valid `KRONOS_DATERANGE` environment variable value -- this will take full precedence if set
        :type named_daterange: str 
        """

        # initialize timezone
        self.tz = None

        if isinstance(start_date, datetime) and isinstance(end_date, datetime):
            # both args are datetimes
            if (start_date.tzinfo is not None and end_date.tzinfo is not None):
                # both args are timezone-aware
                if start_date.tzinfo != end_date.tzinfo:
                    # they do not have the same timezone. convert to the default value of `timezone`, but warn the user.
                    warnings.warn('Your start date and end date have different timezones. Converting to value provided in `timezone` (or default): {}'.format(timezone))
                else:
                    # they have the same timezone! it's settled.
                    self.tz = start_date.tzinfo
            elif bool(start_date.tzinfo) ^ bool(end_date.tzinfo):  # this is a logical XOR. bool is just a subclass of int (1 or 0). bitwise check works here.
                # one of these is timezone-aware. use it
                self.tz = start_date.tzinfo or end_date.tzinfo
            else:
                # neither are timezone-aware. fall back to default.
                self.tz = make_timezone(timezone=timezone)
        elif isinstance(start_date, datetime) or isinstance(end_date, datetime):  # no logical XOR required here
            # one of them is a datetime object
            if timezone:
                # user specified gave us a timezone to convert to. use it
                self.tz = make_timezone(timezone=timezone)
            else:
                # use the one they gave us on the dt object
                self.tz = start_date.tzinfo or end_date.tzinfo
        
        if self.tz is None:
            if not timezone:
                timezone = DEFAULT_TZ
            self.tz = make_timezone(timezone=timezone)

        self.date_format = date_format

        if end_date and not start_date:
            raise AttributeError('Providing an `end_date` without providing a `start_date` is ambiguous. Please provide `start_date` if you want to set `end_date`.')
        
        if named_range is not None:
            start_date, end_date = _get_named_daterange(range_name=named_range, tz=self.tz)
            if start_date is None and end_date is None:
                raise ValueError(f'The value you provided for `named_range=` is not accepted. Please provide a valid `KRONOS_DATERANGE` name (see docs). You sent: `{named_range}`')
        else:
            if not start_date and not end_date:
                # No values were given
                try:
                    start_date, end_date = get_default_daterange(tz=self.tz)
                except ValueError:
                    raise
            else:
                if start_date:
                    # handle start date as either string or datetime object (and localize)
                    start_date = handle_ambiguous_datetime(start_date, self.tz, self.date_format)
                else:
                    # default to yesterday
                    start_date = (datetime.now(tz=self.tz) - timedelta(days=1))

                if end_date:
                    # handle ene date as either string or datetime object (and localize)
                    end_date = handle_ambiguous_datetime(end_date, self.tz, self.date_format)
                else:
                    # default to today
                    end_date = datetime.now(tz=self.tz)

        # set start and end times to midnight if not given in input string
        if not any([start_date.hour, start_date.minute, start_date.second, start_date.microsecond]):
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if not any([end_date.hour, end_date.minute, end_date.second, end_date.microsecond]):
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        if start_date > end_date:
            raise ValueError('`start_date` cannot come after `end_date`.')
        
        self._start_date = start_date
        self._end_date = end_date

    @property
    def start_date(self) -> str:
        return self._start_date.strftime(self.date_format)

    @property
    def end_date(self) -> str:
        return self._end_date.strftime(self.date_format)
    
    @property
    def timezone(self) -> str:
        """ Timezone name set at self.tz """
        return self.tz.zone

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

    @property
    def start_ts(self) -> float:
        """ Get the unix timestamp of the start date

        :return: start_date represented as seconds since the epoch
        :rtype: float
        """
        return self._start_date.timestamp()
    
    @property
    def end_ts(self) -> float:
        """ Get the unix timestamp of the end date

        :return: end_date represented as seconds since the epoch
        :rtype: float
        """
        return self._end_date.timestamp()

    @property
    def start_isoformat(self) -> str:
        """ Start date formatted as ISO-8601. """
        return self._start_date.isoformat()
    
    @property
    def end_isoformat(self) -> str:
        """ End date formatted as ISO-8601. """
        return self._end_date.isoformat()

    def set_start_time(self, hour: int = None, minute: int = None, second: int = None, microsecond: int = None):
        """ Set the time component for the start date late. Return `self`. """
        kwargs = {'hour': hour, 'minute': minute, 'second': second, 'microsecond': microsecond}
        self._start_date = self._start_date.replace(**{k: v for k, v in kwargs.items() if v})
        return self
    
    def set_end_time(self, hour: int = None, minute: int = None, second: int = None, microsecond: int = None):
        """ Set the time component for the end date late. Return `self`. """
        kwargs = {'hour': hour, 'minute': minute, 'second': second, 'microsecond': microsecond}
        self._end_date = self._end_date.replace(**{k: v for k, v in kwargs.items() if v})
        return self

    def change_timezone(self, tz: Union[pytz.BaseTzInfo, str]) -> Kronos:
        """ Switch the timezone of the Kronos object without adjusting the time.

        :param tz: either a pre-built BaseTzInfo object or a timezone name as string
        :type tz: Union[pytz.BaseTzInfo, str]
        :returns: self
        """
        timezone = make_timezone(tz)
        self._start_date = self._start_date.replace(tzinfo=timezone)
        self._end_date = self._end_date.replace(tzinfo=timezone)
        self.tz = timezone
        return self
    
    def parse_and_localize(self, dt_str: str, date_format: str, in_tz: Union[pytz.BaseTzInfo, str] = 'UTC', out_tz: Union[pytz.BaseTzInfo, str] = DEFAULT_TZ) -> datetime:
        """ Create a datetime object from input, set its timezone, and convert it to a new object.

        :param dt_str: a string-represented date
        :type dt_str: str
        :param date_format: the datetime format of `dt_str`
        :type date_format: str
        :param in_tz: input timezone, defaults to 'UTC'
        :type in_tz: Union[pytz.BaseTzInfo, str], optional
        :param out_tz: output timezone, defaults to DEFAULT_TZ
        :type out_tz: Union[pytz.BaseTzInfo, str], optional
        :return: original date string as a datetime object in the new timezone, `out_tz`.
        :rtype: datetime
        """
        return convert_timezone(datetime.strptime(dt_str, date_format), in_tz=in_tz, out_tz=out_tz)

    @staticmethod
    def convert_date(dt_str: str, in_format: str, out_format: str) -> str:
        """ Convert a date in format `in_format` and return string in format `out_format`.

        :param dt_str: a string-representation of a datetime
        :type dt_str: str
        :param in_format: the input dt_str format
        :type in_format: str
        :param out_format: the desired output date format
        :type out_format: str
        :return: string-represented date in specified format
        :rtype: str
        """
        parsed_date = datetime.strptime(dt_str, in_format)
        return parsed_date.strftime(out_format)

    @staticmethod
    def from_timestamp(unix_timestamp) -> datetime:
        """ Convenience pass-thru to datetime.fromtimestamp(...). Returns a datetime object. """
        return datetime.fromtimestamp(unix_timestamp)

    def day_range(self) -> Generator[Kronos]:
        """ Yield one-day Kronos objects for each date between object's start and end date.

        :yield: a one-day Kronos object for each date between self's start and end date
        :rtype: Generator[Kronos]
        """
        for day in rrule(DAILY, dtstart=self._start_date, until=self._end_date):
            day = day.replace(tzinfo=self.tz)
            if day.date() > self._end_date.date():
                # I have no idea why this would be true, but it was...Kronos(start_date='2022-11-03', end_date='2022-11-08' ... ).day_range() was yielding a record for 2022-11-09. TODO: investigate this further
                continue
            if day.strftime(self.date_format) == self.start_date:
                # change _end_date time to 29:59:59
                ed = day.replace(hour=23, minute=59, second=59, microsecond=999999)
                yield self.__class__(day.strftime(self.date_format), ed.strftime(self.date_format), date_format=self.date_format, timezone=self.tz)
            elif day.strftime('%Y-%m-%d') == self.format_end('%Y-%m-%d'):
                # change _start_date time to 00:00:00
                # rrule uses the value of dtstart to carry over time parameters to each entry in the iterable. must ovveride with _end_date
                sd = day.replace(hour=0, minute=0, second=0, microsecond=0)
                ed = day.replace(hour=self._end_date.hour, minute=self._end_date.minute, second=self._end_date.second, microsecond=self._end_date.microsecond)
                yield self.__class__(sd.strftime(self.date_format), ed.strftime(self.date_format), date_format=self.date_format, timezone=self.tz)
            else:
                # set new object's _start_date time to 00:00:00, and 23:59:59 for _end_date
                sd = day.replace(hour=0, minute=0, second=0, microsecond=0)
                ed = day.replace(hour=23, minute=59, second=59, microsecond=999999)
                yield self.__class__(sd.strftime(self.date_format), ed.strftime(self.date_format), date_format=self.date_format, timezone=self.tz)

    def now(self, timezone: Union[pytz.BaseTzInfo, str] = None) -> datetime:
        """ Convenience func to return current local time specified by `timezone`. 
        
        :param timezone: (optional) timezone. returned as `self.tz` if not provided.
        :return: datetime object
        """
        if timezone:
            tz = make_timezone(timezone=timezone)
        else:
            tz = self.tz

        return datetime.now(tz=tz)

    def last_x_days(self, x: int = 30) -> Kronos:
        """ Get the last `x` days since today.

        :param x: number of days to go back, defaults to 30
        :type x: int, optional
        """
        start_date = self.now() - timedelta(days=x)
        return self.__class__(start_date=start_date.strftime('%Y-%m-%d'), end_date=self.now().strftime('%Y-%m-%d'))
    
    def list_date_range(self) -> List[datetime]:
        """ List all dates in the Kronos daterange as datetime objects.

        :return: a list of each day in the range
        :rtype: List[datetime]
        """
        return list(rrule(freq=DAILY, dtstart=self._start_date, until=self._end_date))

    def format_start(self, out_format: str) -> str:
        """ Return start date in specified format.

        :param out_format: a valid strftime format
        :return: start date string in out_format
        """
        return self._start_date.strftime(out_format)

    def format_end(self, out_format: str) -> str:
        """ Return end date in specified format.

        :param out_format: a valid strftime format
        :return: end date string in out_format
        """
        return self._end_date.strftime(out_format)

    def shift_start_tz(self, target_tz: Union[pytz.BaseTzInfo, str] = 'UTC') -> datetime:
        """ Shift the start_date timezone from self.tz to a timezone specified by `target_tz`

        :param target_tz: either a pre-built BaseTzInfo object or a timezone name as string
        :type target_tz: Union[pytz.BaseTzInfo, str]
        :return: timezone-aware datetime object
        """
        return self._start_date.astimezone(tz=make_timezone(target_tz))

    def shift_end_tz(self, target_tz: Union[pytz.BaseTzInfo, str] = 'UTC') -> datetime:
        """ Shift the end_date timezone from self.tz to a timezone specified by `target_tz`

        :param target_tz: either a pre-built BaseTzInfo object or a timezone name as string
        :type target_tz: Union[pytz.BaseTzInfo, str]
        :return: timezone-aware datetime object
        """
        return self._end_date.astimezone(tz=make_timezone(target_tz))
    
    def shift_range(self, **kwargs) -> Kronos:
        """ Shift a Kronos daterange back with relative kwargs. Basically this is a convenience 
        exposure of the timedelta functionality.

        NOTE: Users should avoid using time components to adjust here. Prefer to use the `set_start_time` and `set_end_time` methods.

        :param kwargs: key-value pairs to be deconstructed into timedelta(...) kwargs.
        :return: a timedelta-shifted Kronos object.
        :rtype: Kronos
        """
        new_start = (self._start_date + timedelta(**kwargs)).strftime(self.date_format)
        new_end = (self._end_date + timedelta(**kwargs)).strftime(self.date_format)
        return self.__class__(new_start, new_end)
    
    def splice(self, in_dt: Union[datetime, str], fmt: str = DEFAULT_FORMAT) -> Tuple[Kronos, Kronos]:
        """ Bisect a Kronos daterange, returning two Kronos objects: one that starts at the original start date and ends at the input datetime, 
        and another that starts at the input datetime and ends at the original end date, i.e.:

        (Kronos(start_date, `in_dt`), Kronos(`in_dt`, end_date))

        :param in_dt: datetime to be used to bisect the existing Kronos daterange
        :type in_dt: Union[datetime, str]
        :param fmt: if `in_dt` is a string, provide its strftime format string here. defaults to DEFAULT_FORMAT
        :type fmt: str, optional
        :return: two Kronos objects split on the `in_dt`
        :rtype: Tuple[Kronos, Kronos]
        """
        divider = handle_ambiguous_datetime(datetime_item=in_dt, timezone=self.tz, fmt=fmt)
        return Kronos(self._start_date, divider, timezone=self.tz), Kronos(divider, self._end_date, timezone=self.tz)


    def __repr__(self):
        return "{}(start_date='{}', end_date='{}', date_format='{}', timezone='{}')".format(
            self.__class__.__name__, self.start_date, self.end_date, self.date_format, self.tz.zone
        )
