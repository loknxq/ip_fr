"""Демонстрация для защиты не должна изменять рабочий каталог."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


class DemoOrmTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        record = Record.objects.create(
            title="Существующая пластинка",
            artist="Исполнитель",
            genre="Jazz",
            year=1990,
        )
        collection = Collection.objects.create(name="Существующая коллекция")
        CollectionRecord.objects.create(collection=collection, record=record)
        Collection.objects.create(name="Пустая коллекция")
        User.objects.create(name="Пользователь", email="existing@example.com")

    @staticmethod
    def snapshot():
        return {
            model.__name__: list(model.objects.order_by("pk").values())
            for model in (Record, User, Collection, CollectionRecord)
        }

    def test_crud_demonstration_keeps_existing_data_unchanged(self):
        before = self.snapshot()
        output = StringIO()

        call_command("demo_orm", stdout=output)

        self.assertEqual(self.snapshot(), before)
        for step in ("CREATE:", "READ:", "UPDATE:", "DELETE:"):
            self.assertIn(step, output.getvalue())
        self.assertIn("Транзакция отменена", output.getvalue())

    def test_error_rolls_back_partially_created_demo_objects(self):
        before = self.snapshot()
        target = (
            "collections_app.management.commands.demo_orm."
            "CollectionRecord.objects.create"
        )
        with patch(target, side_effect=RuntimeError("Проверка отката")):
            with self.assertRaisesMessage(RuntimeError, "Проверка отката"):
                call_command("demo_orm", stdout=StringIO())

        self.assertEqual(self.snapshot(), before)
