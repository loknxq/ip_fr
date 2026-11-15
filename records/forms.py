"""Проверка пользовательских параметров каталога."""

from datetime import date

from django import forms

from collections_app.models import Collection
from records.models import Record


RECORD_SORTS = {
    "title": ("title", "pk"),
    "artist": ("artist", "year", "title", "pk"),
    "year": ("year", "title", "pk"),
    "-year": ("-year", "title", "pk"),
}


class RecordFilterForm(forms.Form):
    q = forms.CharField(
        label="Поиск", required=False, max_length=200,
        widget=forms.TextInput(attrs={
            "placeholder": "Название / исполнитель",
        }),
    )
    scope = forms.ChoiceField(
        label="Искать в", required=False,
        choices=(
            ("all", "Названиях и исполнителях"),
            ("title", "Названиях"),
            ("artist", "Исполнителях"),
        ),
    )
    genre = forms.ChoiceField(label="Жанр", required=False)
    year_from = forms.IntegerField(
        label="Год от", required=False, min_value=1900,
    )
    year_to = forms.IntegerField(
        label="Год до", required=False, min_value=1900,
    )
    collection = forms.ModelChoiceField(
        label="Коллекция", required=False,
        queryset=Collection.objects.none(), empty_label="Все коллекции",
    )
    known_year = forms.ChoiceField(
        label="Год выпуска", required=False,
        choices=(("", "Любой"), ("1", "Только известный")),
    )
    sort = forms.ChoiceField(
        label="Сортировка", required=False,
        choices=(
            ("title", "По названию"),
            ("artist", "По исполнителю, затем по году"),
            ("year", "Сначала ранние издания"),
            ("-year", "Сначала поздние издания"),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        genres = (
            Record.objects.exclude(genre__isnull=True).exclude(genre="")
            .order_by("genre").values_list("genre", flat=True).distinct()
        )
        self.fields["genre"].choices = [
            ("", "Все жанры"), *((genre, genre) for genre in genres),
        ]
        self.fields["collection"].queryset = Collection.objects.order_by(
            "name", "pk",
        )
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select)
                else "form-control"
            )
        for field_name in ("year_from", "year_to"):
            self.fields[field_name].widget.attrs["max"] = date.today().year

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("year_from"), cleaned.get("year_to")
        for field_name in ("year_from", "year_to"):
            year = cleaned.get(field_name)
            if year is not None and year > date.today().year:
                self.add_error(field_name, "Год не может быть в будущем.")
        if start is not None and end is not None and start > end:
            raise forms.ValidationError(
                "Начало диапазона годов не может быть позже окончания.",
            )
        return cleaned
