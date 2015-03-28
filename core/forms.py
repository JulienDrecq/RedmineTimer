from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username'),
                                                             'required': '', 'tabindex': 1, 'autofocus': '1'}))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                      'placeholder': _('Password'),
                                                                                      'required': '', 'tabindex': 2}))


class IssueForm(forms.Form):
    issue = forms.CharField(label=_('Issue'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                            'placeholder': _('Search issue ...'),
                                                                            'required': '', 'tabindex': 1,
                                                                            'autofocus': '1'}))

    def clean_issue(self):
        data = self.cleaned_data['issue']
        if data[:1] == "#":
            return data[1:]
        return data


class FilterDateForm(forms.Form):
    start_date = forms.DateField(label=_('Start date'), widget=forms.DateInput(attrs={'class': 'form-control',
                                                                                      'placeholder': _('Start date ...'),
                                                                                      'required': '', 'tabindex': 1}))
    end_date = forms.DateField(label=_('End date'), widget=forms.DateInput(attrs={'class': 'form-control',
                                                                                  'placeholder': _('End date ...'),
                                                                                  'required': '', 'tabindex': 2}))


class TimeEntryEdit(forms.Form):
    date = forms.DateField(label=_('Date'), widget=forms.DateInput(attrs={'class': 'form-control',
                                                                          'placeholder': _('Date'), 'required': '',
                                                                          'tabindex': 1, 'autofocus': '1'}))
    time = forms.CharField(label=_('Time'), widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                            'placeholder': _('Time'),
                                                                            'required': '', 'tabindex': 2}))
    comments = forms.CharField(label=_('Comment'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                'placeholder': _('Enter a comment'),
                                                                                'tabindex': 3}), required=False)