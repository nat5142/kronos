
# Kronos


<div align="center">

[![PyPI - Version](https://img.shields.io/pypi/v/kronos-daterange.svg)](https://pypi.python.org/pypi/kronos-daterange)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kronos-daterange.svg)](https://pypi.python.org/pypi/kronos-daterange)
[![Tests](https://github.com/nat5142/kronos/workflows/tests/badge.svg)](https://github.com/nat5142/kronos/actions?workflow=tests)
[![Codecov](https://codecov.io/gh/nat5142/kronos/branch/main/graph/badge.svg)](https://codecov.io/gh/nat5142/kronos)
[![Read the Docs](https://readthedocs.org/projects/nat5142-kronos/badge/)](https://kronos.readthedocs.io/)
[![PyPI - License](https://img.shields.io/pypi/l/kronos-daterange.svg)](https://pypi.python.org/pypi/kronos-daterange)

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


</div>


Kronos makes dateranges easier.


* GitHub repo: <https://github.com/nat5142/kronos.git>
* Documentation: <https://nat5142-kronos.readthedocs.io/>
* Free software: BSD

<br>

## Quickstart
---

Install from pip:

```shell
pip install kronos-daterange
```

Import & basic init:
```python
from kronos import Kronos

kronos = Kronos(start_date='2022-01-01', end_date='2022-01-31')
```

<br>

## Feature Demo
---

```python
# import
from kronos import Kronos

# init --> defaults to range of <yesterday, today> unless otherwise specified by `KRONOS_DATERANGE` environment variable
kronos = Kronos()

# manually set dates
kronos = Kronos(start_date='2022-10-17', end_date='2022-10-23')

# set timezone
kronos = Kronos(timezone='America/New_York') 

# specify date format
kronos = Kronos(start_date='10/20/2022', end_date='10/31/2022', date_format='%m/%d/%Y')

# access start, end dates
kronos = Kronos()
kronos.start_date
# 2022-10-19
kronos.end_date
# 2022-10-20

# `date_format` carries over to properties:
kronos = Kronos(date_format='%m/%d/%Y')
kronos.start_date
# 10/19/2022
kronos.end_date
# 10/20/2022

# format start and end date with new format
kronos.format_start('%Y-%m-%d %H:%M:%S')
# 2022-10-20 00:00:00
kronos.format_end('%Y-%m-%d %H:%M:%S')
# 2022-10-21 23:59:59

# get the current date in specified timezone
kronos = Kronos('America/Los_Angeles')
kronos.current_date
# 2022-10-20
kronos = Kronos('America/Los_Angeles', date_format='%m/%d/%Y')
kronos.current_date
# 10/20/2022

# overwrite your object's timezone without altering the time
kronos = Kronos(timezone='UTC')
kronos.change_timezone(tz='America/New_York')

# relative shift forward/back
kronos = Kronos()
kronos.shift_range(weeks=-1)  # pipes kwargs into timedelta
# Kronos(start_date='2022-10-12', end_date='2022-10-13', ... )
```

<br>

## Defaults/Environment Variables
---

Kronos is prepared to accept the following environment variables:

- `KRONOS_TIMEZONE`, which defaults to UTC if not set. Can often be overridden at method-levels for one-off timezone conversions.
- `KRONOS_FORMAT`, the strptime date format string for your dates.
- `KRONOS_DATERANGE` (see below)

Note that both `KRONOS_TIMEZONE` and `KRONOS_FORMAT` can be set during init as `timezone=` and `date_format=` arguments, respectively.

### `KRONOS_TIMEZONE`:

Can be any valid timezone name (find them at `pytz.all_timezones`)

### `KRONOS_DATERANGE`:

List of accepted values:

- `LATEST`: start/end dates of yesterady/today
- `YESTERDAY_TODAY`: same as `LATEST`
- `LAST_MONTH`: previous calendar month
- `MTD`: month-to-date
- `LAST_{X}_DAYS`: relative range where end_date is today, start date is set X days behind.
- `THIS_WEEK__{X}`: week-to-date starting on previous day of week specified by X. Valid values for X: `SUN, MON, TUES, WED, THURS, FRI, SAT`

<br>

## Credits
---

This package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.

[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage
