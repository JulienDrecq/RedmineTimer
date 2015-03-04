from django import forms
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"), max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username'),
                                                             'required': '', 'tabindex': 1, 'autofocus': '1'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                      'placeholder': _('Password'),
                                                                                      'required': '', 'tabindex': 2}))