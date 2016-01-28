from django import forms
from django.utils.translation import ugettext_lazy as _
from mc2.controllers.base.models import Controller, EnvVariable


class ControllerForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_cmd = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}))
    marathon_cpus = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_mem = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_instances = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Controller
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd')


class EnvVariableForm(forms.ModelForm):
    key = forms.RegexField(
        "^[0-9a-zA-Z_]+$", required=True, error_messages={
            'invalid':
                _("You did not enter a valid key. Please try again.")},
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    value = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = EnvVariable
        fields = ('key', 'value')


EnvVariableInlineFormSet = forms.inlineformset_factory(
    Controller,
    EnvVariable,
    form=EnvVariableForm,
    extra=1,
    can_delete=True,
    can_order=False
)


class ControllerFormHelper(object):

    def __init__(self, data=None, files=None, instance=None,
                 prefix=None, initial={}):
        self.instance = instance
        self.controller_form = ControllerForm(
            data, files,
            instance=instance)
        self.env_formset = EnvVariableInlineFormSet(
            data, files,
            instance=instance,
            prefix='env')

    def __iter__(self):
        yield self.controller_form
        yield self.env_formset

    def is_valid(self):
        return all(form.is_valid() for form in self)

    def save(self):
        return [form.save() for form in self]
