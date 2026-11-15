"""URL существующих пластинок и вычисляемый в SQLite признак ПР10."""

import unicodedata

import records.models

from django.db import migrations, models
from django.utils.text import slugify


_TRANSLITERATION = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k",
     "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts",
     "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"),
))


def populate_slugs(apps, schema_editor):
    Record = apps.get_model("records", "Record")
    queryset = Record.objects.using(schema_editor.connection.alias)
    for record in queryset.order_by("pk").iterator():
        value = f"{record.title} {record.artist}".lower()
        value = "".join(_TRANSLITERATION.get(char, char) for char in value)
        value = unicodedata.normalize("NFKD", value)
        base = slugify(value, allow_unicode=False)[:175].strip("-") or "record"
        # ID гарантирует уникальность даже для одинаковых названий.
        record.slug = f"{base}-{record.pk}"
        record.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("records", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="record",
            name="slug",
            field=models.SlugField(
                "Адрес страницы (slug)", max_length=200,
                blank=True, null=True,
                help_text=(
                    "Формируется автоматически и сохраняется при переименовании."
                ),
            ),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="record",
            name="slug",
            field=models.SlugField(
                "Адрес страницы (slug)", max_length=200,
                blank=True, unique=True,
                help_text=(
                    "Формируется автоматически и сохраняется при переименовании."
                ),
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="is_vintage",
            field=models.GeneratedField(
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
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="year",
            field=models.PositiveIntegerField(
                "Год выпуска", blank=True, null=True, default=0,
                validators=[records.models.validate_release_year],
                help_text=(
                    "1900–текущий год либо 0, если год выпуска неизвестен."
                ),
            ),
        ),
    ]
