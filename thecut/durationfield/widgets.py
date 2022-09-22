# -*- coding: utf-8 -*-


from dateutil.relativedelta import relativedelta
from django.forms.widgets import Select, TextInput
from isodate import duration_isoformat

from . import utils


class RelativeDeltaWidgetMixin(object):
    def _format_value(self, value):

        if isinstance(value, relativedelta):
            duration = utils.convert_relativedelta_to_duration(value)
            value = duration_isoformat(duration)

        return value

    def render(self, name, value, **kwargs):

        value = self._format_value(value)
        return super(RelativeDeltaWidgetMixin, self).render(
            name, value, **kwargs
        )

    def _has_changed(self, initial, data):
        return super(RelativeDeltaWidgetMixin, self)._has_changed(
            self._format_value(initial), data
        )


class RelativeDeltaTextInput(RelativeDeltaWidgetMixin, TextInput):

    pass


class RelativeDeltaSelect(RelativeDeltaWidgetMixin, Select):

    pass
