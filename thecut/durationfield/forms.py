# -*- coding: utf-8 -*-


import isodate
from django.core.exceptions import ValidationError
from django.forms import ChoiceField, Field
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from isodate.isoerror import ISO8601Error

from . import widgets


class RelativeDeltaChoiceField(ChoiceField):

    widget = widgets.RelativeDeltaSelect

    default_error_messages = {
        "invalid": _("This value must be in ISO 8601 Duration format."),
        "unknown_type": _("The value's type could not be converted"),
    }

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

        if isinstance(value, isodate.duration.Duration):
            return value

        try:
            duration = isodate.parse_duration(value)
        except ISO8601Error:
            raise ValidationError(self.default_error_messages["invalid"])

        return duration

    def valid_value(self, value):
        "Check to see if the provided value is a valid choice"
        text_value = force_str(isodate.duration_isoformat(value))
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == force_str(k2):
                        return True
            else:
                if value == k or text_value == force_str(k):
                    return True
        return False


class RelativeDeltaTextInput(Field):

    widget = widgets.RelativeDeltaTextInput
