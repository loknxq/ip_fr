"""Модель виниловой пластинки с постоянным URL и вычисляемым признаком."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .slug_utils import record_slug_base


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
        help_text="1900–текущий год либо 0, если год выпуска неизвестен.",
    )
    slug = models.SlugField(
        "Адрес страницы (slug)",
        max_length=200,
        blank=True,
        unique=True,
        help_text=(
            "Формируется автоматически и сохраняется при переименовании."
        ),
    )
    is_vintage = models.GeneratedField(
        expression=models.Case(
            models.When(
                year__gte=1900, year__lte=1990,
                then=models.Value(True),
            ),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Классическое издание (до 1990 г.)",
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base = record_slug_base(self.title, self.artist)
            slug = base
            index = 2
            matching = type(self).objects.exclude(pk=self.pk)
            while matching.filter(slug=slug).exists():
                suffix = f"-{index}"
                slug = f"{base[:200 - len(suffix)]}{suffix}"
                index += 1
            self.slug = slug
            # Для ранее созданной записи без slug также обновить это поле.
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {
                    "slug",
                }
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("records:record_by_slug", kwargs={"slug": self.slug})
