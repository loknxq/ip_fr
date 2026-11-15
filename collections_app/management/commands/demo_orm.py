"""Безопасная демонстрация CRUD для защиты практической работы № 9."""

from django.core.management.base import BaseCommand
from django.db import transaction

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


class Command(BaseCommand):
    help = (
        "Показать создание, чтение, изменение и удаление объектов через ORM. "
        "Все действия выполняются во временной транзакции с откатом."
    )

    def handle(self, *args, **options):
        self.stdout.write("ПР9: демонстрация ORM на временных объектах.")
        with transaction.atomic():
            try:
                self._demonstrate()
            finally:
                # Откат обязателен и при успешной демонстрации, и при ошибке.
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            "Демонстрация завершена. Транзакция отменена; "
            "исходные данные не изменены."
        ))

    def _demonstrate(self):
        record = Record.objects.create(
            title="Учебная пластинка ПР9",
            artist="Учебный исполнитель",
            genre="Jazz",
            year=2000,
        )
        replacement = Record.objects.create(
            title="Вторая учебная пластинка ПР9",
            artist="Учебный исполнитель",
            genre="Rock",
            year=2001,
        )
        user = User.objects.create(
            name="Учебный пользователь ПР9",
            email="pr9-demo@example.com",
        )
        collection = Collection.objects.create(name="Учебная коллекция ПР9")
        link = CollectionRecord.objects.create(
            collection=collection, record=record,
        )
        self.stdout.write(
            "CREATE: созданы две пластинки, пользователь, "
            "коллекция и связь между коллекцией и пластинкой."
        )

        record = Record.objects.get(pk=record.pk)
        user = User.objects.get(pk=user.pk)
        collection = Collection.objects.get(pk=collection.pk)
        link = CollectionRecord.objects.select_related(
            "collection", "record",
        ).get(pk=link.pk)
        self.stdout.write(
            f"READ: {record}; {user}; {collection}. "
            f"Связь: {link.collection.name} -> {link.record.title}."
        )
        self.stdout.write(
            "Обратные связи: "
            f"collection.records={collection.records.count()}, "
            f"record.collections={record.collections.count()}."
        )

        record.title = "Обновлённая учебная пластинка ПР9"
        record.save(update_fields=["title"])
        user.name = "Обновлённый учебный пользователь ПР9"
        user.save(update_fields=["name"])
        collection.name = "Обновлённая учебная коллекция ПР9"
        collection.save(update_fields=["name"])
        link.record = replacement
        link.save(update_fields=["record"])

        record.refresh_from_db()
        user.refresh_from_db()
        collection.refresh_from_db()
        link.refresh_from_db()
        self.stdout.write(
            f"UPDATE: {record.title}; {user.name}; {collection.name}. "
            f"Связь теперь ведёт к пластинке: {link.record.title}."
        )

        record_ids = [record.pk, replacement.pk]
        user_id = user.pk
        collection_id = collection.pk
        link_id = link.pk
        link.delete()
        collection.delete()
        record.delete()
        replacement.delete()
        user.delete()
        removed = not any((
            Record.objects.filter(pk__in=record_ids).exists(),
            User.objects.filter(pk=user_id).exists(),
            Collection.objects.filter(pk=collection_id).exists(),
            CollectionRecord.objects.filter(pk=link_id).exists(),
        ))
        if not removed:
            raise RuntimeError("Не удалось удалить временные объекты.")
        self.stdout.write(
            "DELETE: временные объекты удалены; "
            "повторный запрос подтверждает их отсутствие."
        )
