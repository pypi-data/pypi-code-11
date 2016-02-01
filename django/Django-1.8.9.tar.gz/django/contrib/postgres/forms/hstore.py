import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.translation import ugettext_lazy as _

__all__ = ['HStoreField']


class HStoreField(forms.CharField):
    """A field for HStore data which accepts JSON input."""
    widget = forms.Textarea
    default_error_messages = {
        'invalid_json': _('Could not load JSON data.'),
    }

    def prepare_value(self, value):
        if isinstance(value, dict):
            return json.dumps(value)
        return value

    def to_python(self, value):
        if not value:
            return {}
        if not isinstance(value, dict):
            try:
                value = json.loads(value)
            except ValueError:
                raise ValidationError(
                    self.error_messages['invalid_json'],
                    code='invalid_json',
                )
        # Cast everything to strings for ease.
        for key, val in value.items():
            value[key] = six.text_type(val)
        return value

    def has_changed(self, initial, data):
        """
        Return True if data differs from initial.
        """
        # For purposes of seeing whether something has changed, None is
        # the same as an empty dict, if the data or initial value we get
        # is None, replace it w/ {}.
        initial_value = self.to_python(initial)
        return super(HStoreField, self).has_changed(initial_value, data)
