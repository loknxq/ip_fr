"""Регрессионные проверки ограничений, связей и ORM CRUD."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


class ModelTests(TestCase):
    def setUp(self):
        self.record = Record.objects.create(
            title="Abbey Road", artist="The Beatles", genre="Rock", year=1969
        )
        self.collection = Collection.objects.create(name="Классика рока")
        self.user = User.objects.create(name="Иван", email="ivan@example.com")
        self.link = CollectionRecord.objects.create(
            collection=self.collection, record=self.record
        )

    def test_forward_and_reverse_relations(self):
        self.assertEqual(self.collection.records.get(), self.record)
        self.assertEqual(self.record.collections.get(), self.collection)
        self.assertEqual(self.collection.record_links.get(), self.link)
        self.assertEqual(self.record.collection_links.get(), self.link)

    def test_select_related_loads_both_foreign_keys_in_one_query(self):
        with self.assertNumQueries(1):
            link = CollectionRecord.objects.select_related(
                "collection", "record"
            ).get(pk=self.link.pk)
            self.assertEqual(link.collection.name, "Классика рока")
            self.assertEqual(link.record.title, "Abbey Road")

    def test_duplicate_pair_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CollectionRecord.objects.create(
                collection=self.collection, record=self.record
            )
        self.assertEqual(CollectionRecord.objects.count(), 1)

    def test_collection_deletion_removes_only_links(self):
        self.collection.delete()
        self.assertFalse(CollectionRecord.objects.exists())
        self.assertTrue(Record.objects.filter(pk=self.record.pk).exists())
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_record_deletion_preserves_collection(self):
        self.record.delete()
        self.assertFalse(CollectionRecord.objects.exists())
        self.assertTrue(
            Collection.objects.filter(pk=self.collection.pk).exists()
        )

    def test_unknown_year_and_genre_are_supported(self):
        for year in (None, 0, 1900, date.today().year):
            with self.subTest(year=year):
                record = Record(title="Издание", artist="Артист", year=year)
                record.genre = None
                record.full_clean()

    def test_invalid_year_is_rejected(self):
        for year in (-1, 1899, date.today().year + 1):
            with self.subTest(year=year), self.assertRaises(ValidationError):
                record = Record(title="Издание", artist="Артист", year=year)
                record.full_clean()

    def test_required_fields_and_email_are_validated(self):
        for obj in (
            Record(title="", artist="Артист"),
            Collection(name=""),
            User(name="Иван", email="wrong-address"),
        ):
            with self.subTest(model=type(obj)), self.assertRaises(
                ValidationError
            ):
                obj.full_clean()

    def test_crud_and_get_missing_multiple_objects(self):
        record = Record.objects.create(title="Новинка", artist="Артист")
        identifier = record.pk
        record.title = "Исправленное название"
        record.save(update_fields=["title"])
        self.assertEqual(
            Record.objects.get(pk=identifier).title, "Исправленное название"
        )
        Record.objects.filter(pk=identifier).update(genre="Jazz")
        record.refresh_from_db()
        self.assertEqual(record.genre, "Jazz")
        with self.assertRaises(Record.MultipleObjectsReturned):
            Record.objects.get()
        record.delete()
        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(pk=identifier)

    def test_user_create_save_read_and_delete(self):
        user = User.objects.create(name="Анна", email="anna@example.com")
        identifier = user.pk
        user.email = "anna.updated@example.com"
        user.save(update_fields=["email"])
        self.assertEqual(
            User.objects.get(pk=identifier).email, "anna.updated@example.com"
        )
        user.delete()
        self.assertFalse(User.objects.filter(pk=identifier).exists())

    def test_collection_crud_and_membership_changes(self):
        collection = Collection.objects.create(name="Новая коллекция")
        identifier = collection.pk
        collection.records.add(self.record)
        self.assertEqual(collection.records.get(), self.record)
        collection.name = "Избранное"
        collection.save(update_fields=["name"])
        self.assertEqual(
            Collection.objects.get(pk=identifier).name, "Избранное"
        )
        collection.records.remove(self.record)
        self.assertFalse(collection.records.exists())
        collection.delete()
        self.assertFalse(Collection.objects.filter(pk=identifier).exists())

    def test_string_representations_are_readable(self):
        self.assertIn("Abbey Road", str(self.record))
        self.assertIn("1969", str(self.record))
        self.assertEqual(str(self.collection), "Классика рока")
        self.assertIn("ivan@example.com", str(self.user))
        self.assertIn("Классика рока", str(self.link))
