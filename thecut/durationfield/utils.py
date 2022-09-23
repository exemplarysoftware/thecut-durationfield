# -*- coding: utf-8 -*-
"""Utility functions to convert back and forth between a ISO 8601
representation as string and time delta object."""
import isodate
from dateutil.relativedelta import relativedelta


def convert_relativedelta_to_duration(delta):
    """Convert a :py:class:`~dateutil.relativedelta.relativedelta`
    to a :py:class:`~isodate.duration.Duration`."""
    return isodate.duration.Duration(
        days=delta.days,
        seconds=delta.seconds,
        microseconds=delta.microseconds,
        minutes=delta.minutes,
        hours=delta.hours,
        months=delta.months,
        years=delta.years,
    )


def convert_duration_to_relativedelta(duration):
    """Convert a :py:class:`~isodate.duration.Duration` or a
    :py:class:`~datetime.timedelta` to a
    :py:class:`~datetime.relativedelta.relativedelta`.

    Note that we lose some accuracy in this conversion. Partial values for
    years and months are cast into integers before applying them to the
    relativedelta.
    """
    delta = relativedelta()

    # Convert years and months to integers before setting them on the
    # relativdelta instance. This allows us to perform arithmetic with the
    # resulting relativeldelta in combination with a datetime. See
    # https://bugs.launchpad.net/dateutil/+bug/1204017 for a description of the
    # bug which makes this workaround necessary.
    if hasattr(duration, "years"):
        delta.years = int(duration.years)

    if hasattr(duration, "months"):
        delta.months = int(duration.months)

    if hasattr(duration, "days"):
        delta.days = duration.days

    # Some `Duration` objects have an associated timedelta.
    if hasattr(duration, "tdelta"):
        delta.seconds = duration.tdelta.seconds
        delta.microseconds = duration.tdelta.microseconds

    # If we have a `timedelta`, we access the seconds and microseconds values
    # directly.
    if hasattr(duration, "seconds"):
        delta.seconds = duration.seconds

    if hasattr(duration, "microseconds"):
        delta.microseconds = duration.microseconds

    return delta

def convert_timedelta_to_relativedelta(td):
    return relativedelta(days=td.days, seconds=td.seconds, microseconds=td.microseconds)

def convert_timedelta_to_duration(delta):
    """Convert a :py:class:`datetime.timedelta` to a :py:class:`~isodate.duration.Duration`."""
    # Using a relativedelta as an intermediary is a good way to end up with a
    # more human-readable duration string as relative delta will e.g. convert
    # 60 seconds to a minute.
    return convert_relativedelta_to_duration(convert_timedelta_to_relativedelta(delta))
