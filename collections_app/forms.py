"""Параметры поиска коллекций."""

from django import forms

from .models import Collection


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


# Разрешённые поля сортировки нельзя принимать напрямую из request.GET.
PLACEMENT_SORTS = {
    "collection": ("collection_name", "record_title", "id"),
    "artist": ("record_artist", "record_title", "id"),
    "year": ("record_year", "record_title", "id"),
    "-year": ("-record_year", "record_title", "id"),
}


class PlacementFilterForm(forms.Form):
    """Безопасные фильтры, поиск и сортировка учёта экземпляров винила."""

    q = forms.CharField(
        label="Название или исполнитель", required=False, max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    collection = forms.ModelChoiceField(
        label="Коллекция", required=False,
        queryset=Collection.objects.none(), empty_label="Все коллекции",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        label="Состояние", required=False,
        choices=(), widget=forms.Select(attrs={"class": "form-select"}),
    )
    year_from = forms.IntegerField(
        label="Год от", required=False, min_value=1900,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    year_to = forms.IntegerField(
        label="Год до", required=False, min_value=1900,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    available_only = forms.BooleanField(
        label="Только доступные для обмена", required=False,
    )
    sort = forms.ChoiceField(
        label="Сортировка", required=False,
        choices=(
            ("collection", "По коллекции"),
            ("artist", "По исполнителю"),
            ("year", "По году (сначала ранние)"),
            ("-year", "По году (сначала поздние)"),
        ), widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        from datetime import date

        from .models import CollectionRecord

        super().__init__(*args, **kwargs)
        self.fields["collection"].queryset = Collection.objects.order_by(
            "name", "pk",
        )
        self.fields["status"].choices = [
            ("", "Все состояния"), *CollectionRecord.Status.choices,
        ]
        for name in ("year_from", "year_to"):
            self.fields[name].max_value = date.today().year
            self.fields[name].widget.attrs["max"] = date.today().year

    def clean(self):
        cleaned = super().clean()
        from datetime import date

        start = cleaned.get("year_from")
        end = cleaned.get("year_to")
        for field_name in ("year_from", "year_to"):
            year = cleaned.get(field_name)
            if year is not None and year > date.today().year:
                self.add_error(field_name, "Год не может быть в будущем.")
        if start is not None and end is not None and start > end:
            raise forms.ValidationError(
                "Год начала диапазона не может быть позже года окончания.",
            )
        return cleaned
