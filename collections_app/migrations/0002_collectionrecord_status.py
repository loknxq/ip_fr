"""Сохранение истории включений винила при введении статусов ПР10."""

from django.db import migrations, models


def populate_status(apps, schema_editor):
    # До ПР10 каждая связь означала реальное присутствие пластинки.
    # Историческая модель исключает импорт новой модели при миграции.
    CollectionRecord = apps.get_model("collections_app", "CollectionRecord")
    CollectionRecord.objects.using(schema_editor.connection.alias).filter(
        status__isnull=True,
    ).update(status="in_collection")


class Migration(migrations.Migration):
    dependencies = [("collections_app", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="collectionrecord",
            name="status",
            field=models.CharField(
                blank=True, null=True, max_length=15,
                verbose_name="Состояние экземпляра",
            ),
        ),
        migrations.RunPython(populate_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="collectionrecord",
            name="status",
            field=models.CharField(
                "Состояние экземпляра",
                max_length=15,
                choices=[
                    ("in_collection", "В коллекции"),
                    ("reserved", "Зарезервирована"),
                    ("removed", "Выведена из коллекции"),
                ],
                default="in_collection",
                help_text=(
                    "В коллекции — доступна; зарезервирована — не для обмена; "
                    "выведена — сохранена только в истории."
                ),
            ),
        ),
    ]
