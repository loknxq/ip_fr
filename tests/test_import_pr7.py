"""Импорт сохраняет данные и связи либо откатывает всю операцию."""

import hashlib
import sqlite3
from contextlib import closing
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


class ImportTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(dir=settings.BASE_DIR)
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "legacy.sqlite"
        with closing(sqlite3.connect(self.source)) as connection, connection:
            connection.executescript(
                "CREATE TABLE records "
                "(id INTEGER, title TEXT, artist TEXT, "
                "genre TEXT, year INTEGER);"
                "CREATE TABLE users (id INTEGER, name TEXT, email TEXT);"
                "CREATE TABLE collections (id INTEGER, name TEXT);"
                "CREATE TABLE collection_records "
                "(collection_id INTEGER, record_id INTEGER);"
            )
            connection.executemany(
                "INSERT INTO records VALUES (?, ?, ?, ?, ?)",
                [
                    (5, "Kind of Blue", "Miles Davis", "Jazz", 1959),
                    (12, "Unknown year", "Artist", None, None),
                ],
            )
            connection.execute(
                "INSERT INTO users VALUES (8, 'Иван', 'ivan@example.com')"
            )
            connection.executemany(
                "INSERT INTO collections VALUES (?, ?)",
                [(3, "Джаз"), (9, "Пустая коллекция")],
            )
            connection.execute("INSERT INTO collection_records VALUES (3, 5)")

    def run_import(self, **options):
        output = StringIO()
        call_command(
            "import_pr7", source=str(self.source), stdout=output, **options
        )
        return output.getvalue()

    def change_source(self, sql, parameters=()):
        with closing(sqlite3.connect(self.source)) as connection, connection:
            connection.execute(sql, parameters)

    def assert_empty_target(self):
        for model in (Record, User, Collection, CollectionRecord):
            self.assertFalse(model.objects.exists(), model.__name__)

    def test_preserves_ids_values_links_and_source_bytes(self):
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.run_import()
        self.assertEqual(set(Record.objects.values_list("pk", flat=True)),
                         {5, 12})
        self.assertEqual(User.objects.get(pk=8).name, "Иван")
        self.assertIsNone(Record.objects.get(pk=12).year)
        self.assertIsNone(Record.objects.get(pk=12).genre)
        self.assertEqual(Collection.objects.get(pk=3).records.get().pk, 5)
        self.assertEqual(Collection.objects.get(pk=9).records.count(), 0)
        self.assertEqual(CollectionRecord.objects.count(), 1)
        self.assertEqual(
            hashlib.sha256(self.source.read_bytes()).hexdigest(), before
        )
        created = Record.objects.create(title="Новая", artist="Исполнитель")
        self.assertGreater(created.pk, 12)

    def test_identical_repeat_import_does_not_duplicate(self):
        self.run_import()
        message = self.run_import()
        self.assertEqual(Record.objects.count(), 2)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Collection.objects.count(), 2)
        self.assertEqual(CollectionRecord.objects.count(), 1)
        self.assertIn("пластинок: 0", message)
        self.assertIn("связей: 0", message)

    def test_conflict_rolls_back_preceding_inserts(self):
        User.objects.create(pk=8, name="Другое имя", email="ivan@example.com")
        with self.assertRaisesMessage(CommandError, "Конфликт User"):
            self.run_import()
        self.assertFalse(Record.objects.exists())
        self.assertFalse(Collection.objects.exists())
        self.assertFalse(CollectionRecord.objects.exists())
        self.assertEqual(User.objects.get(pk=8).name, "Другое имя")

    def test_dangling_relation_rolls_back(self):
        self.change_source("INSERT INTO collection_records VALUES (3, 999)")
        with self.assertRaisesMessage(CommandError, "отсутствующим объектом"):
            self.run_import()
        self.assert_empty_target()

    def test_duplicate_relation_is_reported(self):
        self.change_source("INSERT INTO collection_records VALUES (3, 5)")
        with self.assertRaisesMessage(CommandError, "Дублирующаяся связь"):
            self.run_import()
        self.assert_empty_target()

    def test_duplicate_entity_id_is_reported(self):
        self.change_source(
            "INSERT INTO records SELECT * FROM records WHERE id=5"
        )
        with self.assertRaisesMessage(CommandError, "Дублирующийся"):
            self.run_import()
        self.assert_empty_target()

    def test_invalid_year_does_not_write_partial_data(self):
        self.change_source("UPDATE records SET year=1800 WHERE id=12")
        with self.assertRaisesMessage(CommandError, "Некорректная запись"):
            self.run_import()
        self.assert_empty_target()

    def test_invalid_email_is_reported(self):
        self.change_source("UPDATE users SET email='wrong-address'")
        with self.assertRaisesMessage(CommandError, "Некорректная запись"):
            self.run_import()
        self.assert_empty_target()

    def test_wrong_field_type_is_not_silently_coerced(self):
        self.change_source("UPDATE records SET year='invalid' WHERE id=12")
        with self.assertRaisesMessage(CommandError, "Неверный тип"):
            self.run_import()
        self.assert_empty_target()

    def test_missing_source_does_not_create_a_file(self):
        self.source = Path(self.directory.name) / "missing.sqlite"
        with self.assertRaisesMessage(CommandError, "не найдена"):
            self.run_import()
        self.assertFalse(self.source.exists())
        self.assert_empty_target()

    def test_broken_source_schema_is_reported(self):
        self.change_source("DROP TABLE collection_records")
        with self.assertRaisesMessage(CommandError, "структуру базы ПР7"):
            self.run_import()
        self.assert_empty_target()

    def test_check_only_performs_validation_then_rolls_back(self):
        message = self.run_import(check_only=True)
        self.assertIn("изменения отменены", message)
        self.assertIn("пластинок: 2", message)
        self.assert_empty_target()
