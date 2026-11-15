"""Проверяемые в терминале операции ПР10 без изменения рабочей базы."""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from collections_app.models import Collection, CollectionRecord
from records.models import Record


class Command(BaseCommand):
    help = (
        "Демонстрация QuerySet, TextChoices, F, GeneratedField и SQL; "
        "все тестовые изменения откатываются."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            record = Record.objects.create(
                title="ПР10 Демонстрация", artist="Тестовый исполнитель",
                year=1980, genre="Rock",
            )
            collection = Collection.objects.create(name="ПР10 (временная)")
            placement = CollectionRecord.objects.create(
                collection=collection, record=record,
            )
            record.refresh_from_db()
            self.stdout.write(f"URL: {record.get_absolute_url()}")
            self.stdout.write(f"Классическое издание: {record.is_vintage}")
            is_available = CollectionRecord.objects.available().filter(
                pk=placement.pk,
            ).exists()
            self.stdout.write(f"Доступно: {is_available}")
            placement.status = CollectionRecord.Status.RESERVED
            placement.save(update_fields=["status"])
            is_available = CollectionRecord.objects.available().filter(
                pk=placement.pk,
            ).exists()
            self.stdout.write(f"После резерва доступно: {is_available}")
            queryset = CollectionRecord.objects.for_collection(
                collection,
            ).annotate(
                collection_name=F("collection__name"),
                record_title=F("record__title"),
            ).values("collection_name", "record_title", "status")
            self.stdout.write(f"ORM: {list(queryset)}")
            self.stdout.write(f"SQL: {queryset.query}")
            self.stdout.write(f"План SQL: {queryset.explain()}")
            record.year = 2000
            record.save(update_fields=["year"])
            record.refresh_from_db()
            self.stdout.write(
                f"После изменения года признак классики: {record.is_vintage}"
            )
            placement.status = CollectionRecord.Status.REMOVED
            placement.save(update_fields=["status"])
            is_current = CollectionRecord.objects.current().filter(
                pk=placement.pk,
            ).exists()
            self.stdout.write(
                f"После вывода осталось в коллекции: {is_current}",
            )
            # Демонстрируем CRUD; никакие созданные записи не сохраняются.
            placement.delete()
            collection.delete()
            record.delete()
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            "Транзакция откатилась; рабочие данные не изменены.",
        ))
