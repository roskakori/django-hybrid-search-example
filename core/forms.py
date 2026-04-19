from django import forms
from django.conf import settings

from core import models
from core.models import IsoLanguage


class SearchForm(forms.Form):
    KIND_CHOICES = [
        ("plain", "plain"),
        ("full-text", "full-text"),
        ("semantic", "semantic"),
        ("hybrid", "hybrid"),
    ]

    kind = forms.ChoiceField(
        choices=KIND_CHOICES,
        widget=forms.Select,
        initial="plain",
    )
    iso_language = forms.ChoiceField(
        choices=models.IsoLanguage.choices,
        widget=forms.Select,
        required=False,
        initial=IsoLanguage(settings.LANGUAGE_CODE[:2]),
    )
    term = forms.CharField(required=True)
