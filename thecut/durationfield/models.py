# -*- coding: utf-8 -*-


from datetime import timedelta
from time import time

import isodate
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from isodate.isoerror import ISO8601Error

from . import forms, utils


class ISO8601DurationField(models.Field):
    """Store and retrieve ISO 8601 formatted durations."""

    description = _("A duration of time (ISO 8601 format)")

    default_error_messages = {
        "invalid": _("This value must be in ISO 8601 Duration format."),
        "unknown_type": _("The value's type could not be converted"),
    }

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs["max_length"] = 64
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def deconstruct(self, *args, **kwargs):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def to_python(self, value):
        """
        :returns: A duration object parsed from the given value.
        :rtype: :py:class:`~isodate.duration.Duration`

        """
        # DB value is null
        if value is None:
            return None

        # DB value is empty
        if value == "":
            return None

        if isinstance(value, isodate.duration.Duration) or isinstance(
            value, timedelta
        ) or isinstance(value, timedelta):
            return value

        try:
            duration = isodate.parse_duration(value)
        except ISO8601Error:
            raise ValidationError(self.default_error_messages["invalid"])
        return duration

    def get_prep_value(self, value):
        # Value in DB should be null.
        if value is None:
            return None

        if not isinstance(value, isodate.duration.Duration):
            raise ValidationError(
                "Cannot convert objects that are not Durations."
            )

        return isodate.duration_isoformat(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class RelativeDeltaField(ISO8601DurationField):
    """Store and retrieve :py:class:`~dateutil.relativedelta.relativedelta`.

    Stores the relativedelta as a string representation of a
    :py:class:`~isodate.duration.Duration`.
    """

    def formfield(self, **kwargs):
        defaults = {"form_class": forms.RelativeDeltaChoiceField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def to_python(self, value):
        # If the value is already a relativedelta, return it as-is.
        if isinstance(value, relativedelta):
            return value

        # If the value is a timedelta, convert it to a relativedelta.
        if isinstance(value, timedelta):
            return utils.convert_timedelta_to_relativedelta(timedelta)

        duration = super().to_python(value)

        if duration:
            # type check
            assert isinstance(value, isodate.duration.Duration)
            return utils.convert_duration_to_relativedelta(duration)

    def get_prep_value(self, value):
        # Value in DB should be null
        if value is None:
            return None

        # Build the Duration object from the given relativedelta.
        if isinstance(value, relativedelta):
            duration = utils.convert_relativedelta_to_duration(value)
        elif isinstance(value, timedelta):
            duration = utils.convert_timedelta_to_duration(value)

        # We have a Duration object. We can use the parent class's method to
        # convert it to a string.
        return super().get_prep_value(duration)

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        s = self.get_prep_value(val)
        return "" if s is None else s
