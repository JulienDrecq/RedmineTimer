from django import forms
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"), max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username'),
                                                             'required': '', 'tabindex': 1, 'autofocus': '1'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                      'placeholder': _('Password'),
                                                                                      'required': '', 'tabindex': 2}))


class IssueForm(forms.Form):
    issue = forms.CharField(label=_("Issue"), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                            'placeholder': _('Search issue ...'),
                                                                            'required': '', 'tabindex': 1,
                                                                            'autofocus': '1'}))

    def clean_issue(self):
        data = self.cleaned_data['issue']
        if data[:1] == "#":
            return data[1:]
        return data