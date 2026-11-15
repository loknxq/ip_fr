"""Модель пластинки для текущего Django-приложения."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


def validate_release_year(value):
    """Нулевой/неуказанный год сохранён для совместимости с ПР7."""
    if value not in (None, 0) and not 1900 <= value <= date.today().year:
        raise ValidationError(
            "Укажите год от 1900 до %(year)s или 0, если он неизвестен.",
            params={"year": date.today().year},
        )


class Record(models.Model):
    title = models.CharField("Название", max_length=255)
    artist = models.CharField("Исполнитель", max_length=255)
    genre = models.CharField(
        "Жанр", max_length=255, blank=True, null=True, default=""
    )
    year = models.PositiveIntegerField(
        "Год выпуска",
        blank=True,
        null=True,
        default=0,
        validators=[validate_release_year],
    )

    class Meta:
        ordering = ["title", "pk"]
        verbose_name = "пластинка"
        verbose_name_plural = "пластинки"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(year__isnull=True)
                    | models.Q(year=0)
                    | models.Q(year__gte=1900)
                ),
                name="record_year_unknown_or_modern",
            ),
        ]

    @property
    def display_name(self):
        year = f", {self.year}" if self.year else ""
        return f"{self.title} — {self.artist}{year}"

    def __str__(self):
        return self.display_name
