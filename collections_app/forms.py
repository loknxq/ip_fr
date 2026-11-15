"""Параметры поиска коллекций."""

from django import forms


class CollectionSearchForm(forms.Form):
    q = forms.CharField(
        label="Название коллекции", required=False, max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control", "placeholder": "Поиск по названию",
        }),
    )

    artist = forms.CharField(
        label="Пластинки исполнителя", required=False, max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control", "placeholder": "Любой исполнитель",
        }),
    )
