"""ПР10: статусы экземпляров винила, Django Admin, slug, ORM и миграции."""

from datetime import date
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.contrib import admin
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


class NextPageLink(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag == "a" and dict(attrs).get("rel") == "next":
            self.href = dict(attrs)["href"]


class PR10ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.collection = Collection.objects.create(name="Коллекция рока")
        cls.other = Collection.objects.create(name="Джаз и классика")
        cls.early = Record.objects.create(
            title="Ёжик", artist="Мелодия", year=1975, genre="Rock",
        )
        cls.later = Record.objects.create(
            title="New Sound", artist="Artist", year=2001, genre="Rock",
        )
        cls.unknown = Record.objects.create(
            title="Без даты", artist="Мелодия", year=0, genre="",
        )
        cls.available = CollectionRecord.objects.create(
            collection=cls.collection, record=cls.early,
        )
        cls.reserved = CollectionRecord.objects.create(
            collection=cls.collection, record=cls.later,
            status=CollectionRecord.Status.RESERVED,
        )
        cls.removed = CollectionRecord.objects.create(
            collection=cls.other, record=cls.unknown,
            status=CollectionRecord.Status.REMOVED,
        )

    def test_cyrillic_slug_get_absolute_url_and_legacy_route(self):
        self.assertTrue(self.early.slug.startswith("yozhik-melodiya"))
        self.assertRegex(self.early.slug, r"^[a-z0-9-]+$")
        self.assertEqual(
            self.early.get_absolute_url(),
            reverse("records:record_by_slug", args=[self.early.slug]),
        )
        for url in (
            self.early.get_absolute_url(),
            reverse("records:record_detail", args=[self.early.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.early.title)
        self.assertContains(
            self.client.get(reverse("records:records")),
            self.early.get_absolute_url(),
        )
        self.assertEqual(
            self.client.get(reverse(
                "records:record_by_slug", args=["unknown-record"],
            )).status_code,
            404,
        )

    def test_slug_collision_and_renaming_preserves_link(self):
        duplicate = Record.objects.create(
            title=self.early.title, artist=self.early.artist, year=1981,
        )
        self.assertNotEqual(duplicate.slug, self.early.slug)
        original = duplicate.slug
        duplicate.title = "Переиздание"
        duplicate.save(update_fields=["title"])
        duplicate.refresh_from_db()
        self.assertEqual(duplicate.slug, original)
        self.assertEqual(
            self.client.get(duplicate.get_absolute_url()).status_code, 200,
        )

    def test_generated_field_is_computed_and_updated_in_database(self):
        self.early.refresh_from_db()
        self.later.refresh_from_db()
        self.unknown.refresh_from_db()
        self.assertTrue(self.early.is_vintage)
        self.assertFalse(self.later.is_vintage)
        self.assertFalse(self.unknown.is_vintage)
        self.early.year = 1999
        self.early.save(update_fields=["year"])
        self.early.refresh_from_db()
        self.assertFalse(self.early.is_vintage)
        self.early.year = date.today().year
        self.early.save(update_fields=["year"])
        self.early.refresh_from_db()
        self.assertFalse(self.early.is_vintage)

    def test_querysets_have_consistent_status_business_rules(self):
        qs = CollectionRecord.objects
        self.assertEqual(qs.current().count(), 2)
        self.assertEqual(list(qs.available()), [self.available])
        self.assertEqual(list(qs.reserved()), [self.reserved])
        self.assertEqual(list(qs.removed()), [self.removed])
        self.assertEqual(qs.for_year(1975).get(), self.available)
        self.assertEqual(
            qs.for_collection(self.collection).count(), 2,
        )
        self.assertEqual(qs.for_record(self.unknown).count(), 1)
        self.reserved.status = CollectionRecord.Status.IN_COLLECTION
        self.reserved.save(update_fields=["status"])
        self.assertEqual(qs.available().count(), 2)
        self.removed.status = CollectionRecord.Status.RESERVED
        self.removed.save(update_fields=["status"])
        self.assertEqual(qs.current().count(), 3)

    def test_statuses_affect_public_lists_and_statistics(self):
        response = self.client.get(reverse("collections_app:statistics"))
        self.assertEqual(response.context["status_counts"], {
            "current": 2, "available": 1, "reserved": 1, "removed": 1,
        })
        self.assertEqual(response.context["stats"]["total_links"], 3)
        self.assertEqual(response.context["uncollected_count"], 1)
        self.assertContains(response, "Зарезервированы")
        collection = self.client.get(reverse(
            "collections_app:collection_detail", args=[self.collection.pk],
        ))
        self.assertContains(collection, "Резерв")
        self.assertEqual(len(collection.context["records"]), 2)
        removed_collection = self.client.get(reverse(
            "collections_app:collection_detail", args=[self.other.pk],
        ))
        self.assertEqual(removed_collection.context["records"], [])
        # После отмены резерва экземпляр снова доступен для обмена.
        self.reserved.status = CollectionRecord.Status.IN_COLLECTION
        self.reserved.save(update_fields=["status"])
        response = self.client.get(reverse("collections_app:statistics"))
        self.assertEqual(response.context["status_counts"]["available"], 2)

    def test_record_detail_filters_its_own_membership_without_duplicates(self):
        # В одной коллекции есть действующие экземпляры и выведенный.
        # Нельзя показывать коллекцию выведенной пластинки из-за
        # другой, действующей пластинки той же коллекции.
        CollectionRecord.objects.create(
            collection=self.collection, record=self.unknown,
            status=CollectionRecord.Status.REMOVED,
        )
        removed_response = self.client.get(self.unknown.get_absolute_url())
        self.assertEqual(removed_response.context["collections"], [])
        current_response = self.client.get(self.early.get_absolute_url())
        self.assertEqual(
            [item.pk for item in current_response.context["collections"]],
            [self.collection.pk],
        )

    def test_catalog_filter_excludes_removed_membership(self):
        url = reverse("records:records")
        response = self.client.get(url, {"collection": self.other.pk})
        self.assertEqual(response.context["page_obj"].paginator.count, 0)
        response = self.client.get(url, {"collection": self.collection.pk})
        self.assertEqual(response.context["page_obj"].paginator.count, 2)

    def test_placements_filter_values_f_and_sql_join(self):
        url = reverse("collections_app:placements")
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                url, {"status": "reserved", "q": "Artist", "sort": "year"},
            )
            rows = list(response.context["placements"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["record_title"], "New Sound")
        self.assertEqual(rows[0]["collection_name"], self.collection.name)
        self.assertEqual(rows[0]["record_artist"], "Artist")
        self.assertEqual(rows[0]["status"], "reserved")
        sqls = [entry["sql"] for entry in queries.captured_queries]
        projected = [
            sql for sql in sqls
            if 'AS "record_title"' in sql
            and 'AS "collection_name"' in sql
        ]
        self.assertEqual(len(projected), 1)
        self.assertIn('JOIN "records_record"', projected[0])
        self.assertIn('JOIN "collections_app_collection"', projected[0])

    def test_invalid_parameters_do_not_cause_http_500(self):
        url = reverse("collections_app:placements")
        for params in (
            {"collection": "wrong"},
            {"status": "invalid"},
            {"year_from": "abc"},
            {"year_from": "1899"},
            {"year_to": str(date.today().year + 1)},
            {"year_from": "2000", "year_to": "1900"},
            {"sort": "record__artist; DROP TABLE users_user"},
            {"q": "a" * 201},
        ):
            with self.subTest(params=params):
                response = self.client.get(url, params)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertEqual(
                    response.context["page_obj"].paginator.count, 0,
                )
        self.assertEqual(CollectionRecord.objects.count(), 3)

    def test_filter_sort_and_pagination_preserve_querystring(self):
        for index in range(9):
            record = Record.objects.create(
                title=f"Archive {index:02}", artist="Artist",
                year=1980 + index,
            )
            CollectionRecord.objects.create(
                collection=self.collection, record=record,
            )
        url = reverse("collections_app:placements")
        params = {
            "q": "Artist", "collection": str(self.collection.pk),
            "status": CollectionRecord.Status.IN_COLLECTION,
            "sort": "-year", "year_from": "1970",
        }
        response = self.client.get(url, params)
        self.assertEqual(response.context["page_obj"].paginator.count, 9)
        self.assertEqual(len(response.context["placements"]), 5)
        parser = NextPageLink()
        parser.feed(response.content.decode())
        self.assertIsNotNone(parser.href)
        self.assertEqual(
            parse_qs(urlsplit(parser.href).query),
            {**{key: [value] for key, value in params.items()}, "page": ["2"]},
        )
        following = self.client.get(url + parser.href)
        self.assertEqual(following.context["page_obj"].number, 2)
        self.assertEqual(len(following.context["placements"]), 4)
        self.assertEqual(
            following.context["form"]["sort"].value(), "-year",
        )

    def test_placement_detail_uses_select_related_and_has_404(self):
        url = reverse(
            "collections_app:placement_detail", args=[self.available.pk],
        )
        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(url)
        self.assertContains(response, self.early.title)
        self.assertContains(response, self.collection.name)
        selects = [
            item["sql"] for item in captured.captured_queries
            if "SELECT" in item["sql"]
        ]
        detail_selects = [
            sql for sql in selects
            if 'FROM "collections_app_collectionrecord"' in sql
        ]
        self.assertEqual(len(detail_selects), 1)
        self.assertIn('JOIN "records_record"', detail_selects[0])
        self.assertIn('JOIN "collections_app_collection"', detail_selects[0])
        self.assertEqual(
            self.client.get(reverse(
                "collections_app:placement_detail", args=[9999999],
            )).status_code, 404,
        )

    def test_context_processor_available_on_multiple_pages(self):
        pages = (
            reverse("homepage:index"), reverse("records:records"),
            reverse("collections_app:placements"),
        )
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.context["site_name"], "Vinyl Collection Service",
                )
                self.assertEqual(response.context["records_count"], 3)
                self.assertContains(response, "Пластинки (3)")


class PR10AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.record = Record.objects.create(
            title="Classic", artist="Artist", year=1970,
        )
        cls.collection = Collection.objects.create(name="Vinyl")
        cls.placement = CollectionRecord.objects.create(
            collection=cls.collection, record=cls.record,
        )

    def test_all_domain_models_registered_and_inlines_available(self):
        for model in (Record, Collection, CollectionRecord, User):
            self.assertIn(model, admin.site._registry)
        self.assertEqual(
            admin.site._registry[CollectionRecord].list_select_related,
            ("collection", "record"),
        )
        self.assertEqual(
            admin.site._registry[Record].inlines[0].model,
            CollectionRecord,
        )
        self.assertEqual(
            admin.site._registry[Collection].inlines[0].model,
            CollectionRecord,
        )
        self.assertNotEqual(get_user_model(), User)

    def test_admin_lists_search_filter_and_inline_pages(self):
        admin_user = get_user_model().objects.create_superuser(
            username="supervisor", email="supervisor@example.com",
            password="Strong-Password-12345",
        )
        self.client.force_login(admin_user)
        urls = (
            reverse("admin:records_record_changelist"),
            reverse("admin:collections_app_collection_changelist"),
            reverse("admin:collections_app_collectionrecord_changelist"),
            reverse("admin:users_user_changelist"),
            reverse("admin:records_record_change", args=[self.record.pk]),
            reverse(
                "admin:collections_app_collection_change",
                args=[self.collection.pk],
            ),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(
            self.client.get(reverse(
                "admin:collections_app_collectionrecord_changelist",
            ), {"q": "Classic", "status__exact": "in_collection"}),
            "Classic",
        )

    def test_admin_action_changes_status_and_preserves_link(self):
        self.client.force_login(get_user_model().objects.create_superuser(
            username="root", email="root@example.com",
            password="Strong-Password-12345",
        ))
        url = reverse("admin:collections_app_collectionrecord_changelist")
        response = self.client.post(url, {
            "action": "mark_reserved",
            "_selected_action": [self.placement.pk],
            "index": "0",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.placement.refresh_from_db()
        self.assertEqual(
            self.placement.status, CollectionRecord.Status.RESERVED,
        )
        self.assertEqual(CollectionRecord.objects.count(), 1)

    def test_staff_group_cannot_delete_records_without_permission(self):
        group = Group.objects.create(name="Операторы пластинок")
        group.permissions.set(Permission.objects.filter(
            content_type__app_label="records", codename__in=(
                "view_record", "add_record", "change_record",
            ),
        ))
        operator = get_user_model().objects.create_user(
            username="operator", password="Strong-Password-12345",
            is_staff=True,
        )
        operator.groups.add(group)
        self.client.force_login(operator)
        self.assertEqual(
            self.client.get(reverse("admin:records_record_changelist"))
            .status_code, 200,
        )
        self.assertEqual(
            self.client.get(reverse(
                "admin:records_record_delete", args=[self.record.pk],
            )).status_code, 403,
        )


class PR10FixtureTests(TestCase):
    def test_legacy_fixture_restores_records_with_unique_slug_and_status(self):
        call_command(
            "loaddata", str(settings.BASE_DIR / "data" / "orm_fixture.json"),
            verbosity=0,
        )
        self.assertEqual(Record.objects.count(), 10)
        self.assertEqual(Collection.objects.count(), 5)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(CollectionRecord.objects.count(), 13)
        self.assertEqual(
            CollectionRecord.objects.available().count(), 13,
        )
        self.assertEqual(
            Record.objects.exclude(slug="").count(), 10,
        )
        self.assertEqual(
            Record.objects.values("slug").distinct().count(), 10,
        )
        self.assertTrue(Record.objects.get(pk=1).is_vintage)
        self.assertFalse(Record.objects.get(pk=10).is_vintage)
