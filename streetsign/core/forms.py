from django import forms
from django.utils.translation import gettext as _

class NewFeedForm(forms.Form):
    name = forms.CharField(label=_('Feed Name'))
