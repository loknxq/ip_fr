"""Регрессия страниц ПР7 и сценарии ORM из ПР9."""

from datetime import date
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.next_url = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("rel") == "next":
            self.next_url = attributes["href"]


class ORMViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.abbey = Record.objects.create(
            title="Abbey Road", artist="The Beatles", genre="Rock", year=1969,
        )
        cls.wall = Record.objects.create(
            title="The Wall", artist="Pink Floyd",
            genre="Progressive Rock", year=1979,
        )
        cls.wish = Record.objects.create(
            title="Wish You Were Here", artist="Pink Floyd",
            genre="Progressive Rock", year=1975,
        )
        cls.jazz = Record.objects.create(
            title="Kind of Blue", artist="Miles Davis",
            genre="Jazz", year=1959,
        )
        cls.unknown = Record.objects.create(
            title="Unknown", artist="Unknown Artist", genre=None, year=0,
        )
        cls.no_year = Record.objects.create(
            title="No Year", artist="Another Artist", genre="", year=None,
        )
        cls.compilation = Record.objects.create(
            title="The Beatles Story", artist="Compilation",
            genre="Rock", year=2000,
        )
        cls.extra_records = [
            Record.objects.create(
                title=f"Rock Anthology {index:02}", artist="Zed",
                genre="Rock", year=1980 + index,
            )
            for index in range(7)
        ]
        cls.rock = Collection.objects.create(name="Rock favorites")
        cls.rock.records.add(
            cls.abbey, cls.wall, cls.wish, cls.compilation, *cls.extra_records,
        )
        cls.empty = Collection.objects.create(name="Empty collection")
        cls.jazz_collection = Collection.objects.create(name="Evening jazz")
        cls.jazz_collection.records.add(cls.jazz)
        User.objects.create(name="Иван", email="ivan@example.com")
        User.objects.create(name="Анна", email="anna@example.com")

    def catalog(self, **params):
        return self.client.get(reverse("records:records"), params)

    def record_ids(self, response):
        return [record.pk for record in response.context["records"]]

    def test_previous_pages_are_available(self):
        names = [
            "homepage:index", "records:records", "records:search",
            "collections_app:collections", "collections_app:statistics",
        ]
        for name in names:
            with self.subTest(url=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_catalog_is_ordered_and_has_five_items_per_page(self):
        first, second = self.catalog(), self.catalog(page=2)
        self.assertEqual(first.context["page_obj"].paginator.count, 14)
        self.assertEqual(len(self.record_ids(first)), 5)
        self.assertEqual(len(self.record_ids(second)), 5)
        overlap = set(self.record_ids(first)) & set(self.record_ids(second))
        self.assertFalse(overlap)
        names = [record.title for record in first.context["records"]]
        self.assertEqual(names, sorted(names))

    def test_search_uses_title_or_artist_and_scopes(self):
        cases = [
            ({"q": " pink "}, [self.wall.pk, self.wish.pk]),
            ({"q": "beatles", "scope": "title"}, [self.compilation.pk]),
            ({"q": "beatles", "scope": "artist"}, [self.abbey.pk]),
        ]
        for params, expected in cases:
            with self.subTest(params=params):
                response = self.client.get(reverse("records:search"), params)
                self.assertEqual(self.record_ids(response), expected)

    def test_search_without_text_does_not_return_entire_catalog(self):
        response = self.client.get(reverse("records:search"), {"q": "  "})
        self.assertEqual(self.record_ids(response), [])
        self.assertContains(response, "Введите название пластинки")

    def test_single_filter_and_year_range(self):
        self.assertEqual(self.record_ids(self.catalog(genre="Jazz")), [
            self.jazz.pk,
        ])
        response = self.catalog(year_from=1970, year_to=1980, sort="year")
        self.assertEqual(self.record_ids(response), [
            self.wish.pk, self.wall.pk, self.extra_records[0].pk,
        ])

    def test_related_collection_filter_does_not_duplicate_records(self):
        # Одна пластинка входит в две коллекции, но не повторяется в каталоге.
        self.jazz_collection.records.add(self.abbey)
        response = self.catalog(collection=self.rock.pk)
        self.assertEqual(response.context["page_obj"].paginator.count, 11)
        self.assertNotIn(self.jazz.pk, self.record_ids(response))
        self.assertEqual(len(self.record_ids(response)), 5)

    def test_exclude_unknown_years(self):
        response = self.catalog(known_year="1", sort="year")
        self.assertEqual(response.context["page_obj"].paginator.count, 12)
        self.assertEqual(self.record_ids(response)[0], self.jazz.pk)
        self.assertTrue(all(
            record.year for record in response.context["records"]
        ))

    def test_sort_by_several_fields(self):
        response = self.catalog(sort="artist", known_year="1")
        self.assertEqual(self.record_ids(response)[:5], [
            self.compilation.pk, self.jazz.pk, self.wish.pk,
            self.wall.pk, self.abbey.pk,
        ])

    def test_reverse_year_sort_and_one_sided_ranges(self):
        response = self.catalog(year_from=1984, sort="-year")
        self.assertEqual(self.record_ids(response), [
            self.compilation.pk, self.extra_records[6].pk,
            self.extra_records[5].pk, self.extra_records[4].pk,
        ])
        self.assertEqual(self.record_ids(self.catalog(year_to=1960)), [
            self.jazz.pk,
        ])

    def test_search_filters_and_sort_survive_page_transition(self):
        params = {
            "q": "Rock", "scope": "title", "genre": "Rock",
            "year_from": "1980", "year_to": "2020",
            "collection": str(self.rock.pk), "known_year": "1",
            "sort": "-year",
        }
        response = self.catalog(**params)
        self.assertEqual(response.context["page_obj"].paginator.count, 7)
        parser = LinkParser()
        parser.feed(response.content.decode())
        self.assertIsNotNone(parser.next_url)
        query = parse_qs(urlsplit(parser.next_url).query)
        self.assertEqual(query, {key: [value] for key, value in {
            **params, "page": "2",
        }.items()})
        next_response = self.client.get(
            reverse("records:records") + parser.next_url,
        )
        self.assertEqual(self.record_ids(next_response), [
            self.extra_records[1].pk, self.extra_records[0].pk,
        ])
        selected_sort = next_response.context["form"]["sort"].value()
        self.assertEqual(selected_sort, "-year")
        self.assertNotContains(response, 'name="page"')

    def test_invalid_filter_parameters_show_errors_without_server_error(self):
        cases = [
            {"year_from": "abc"}, {"year_to": "-1"},
            {"year_from": str(date.today().year + 1)},
            {"year_from": "2000", "year_to": "1900"},
            {"sort": "title); DROP TABLE records_record;--"},
            {"genre": "Несуществующий жанр"}, {"scope": "bad-field"},
            {"collection": "abc"}, {"collection": "99999999"},
            {"collection": "9223372036854775808"},
            {"known_year": "wrong"}, {"q": "x" * 201},
        ]
        for params in cases:
            with self.subTest(params=params):
                response = self.catalog(**params)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertEqual(self.record_ids(response), [])
                self.assertContains(response, "Исправьте параметры поиска")
        self.assertEqual(Record.objects.count(), 14)

    def test_invalid_page_numbers_use_safe_first_or_last_page(self):
        cases = [("abc", 1), ("0", 3), ("-4", 3), ("999999", 3)]
        for value, expected in cases:
            with self.subTest(page=value):
                response = self.catalog(page=value)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["page_obj"].number, expected)

    def test_empty_search_and_sql_metacharacters_are_literal(self):
        for text in ["No such album", "%", "_", "' OR 1=1; --"]:
            with self.subTest(query=text):
                response = self.catalog(q=text)
                self.assertEqual(self.record_ids(response), [])
                self.assertContains(response, "Пластинки не найдены")

    def test_user_text_is_html_escaped(self):
        value = '<script>alert("test")</script>'
        response = self.client.get(reverse("records:search"), {"q": value})
        self.assertNotContains(response, value)
        self.assertContains(response, "&lt;script&gt;")

    def test_details_and_related_objects_need_two_queries(self):
        self.jazz_collection.records.add(self.abbey)
        # ПР10: +1 фиксированный COUNT для общей навигации.
        with self.assertNumQueries(3):
            response = self.client.get(reverse(
                "records:record_detail", args=[self.abbey.pk],
            ))
        self.assertContains(response, "Rock favorites")
        self.assertContains(response, "Evening jazz")
        # ПР10: +1 фиксированный COUNT для общей навигации.
        with self.assertNumQueries(3):
            response = self.client.get(reverse(
                "collections_app:collection_detail", args=[self.rock.pk],
            ))
        self.assertContains(response, "The Wall")
        self.assertEqual(len(response.context["records"]), 11)

    def test_missing_objects_return_404(self):
        for name in [
            "records:record_detail", "collections_app:collection_detail",
        ]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=[999999]))
                self.assertEqual(response.status_code, 404)

    def test_empty_collections_remain_in_lists_statistics_and_details(self):
        response = self.client.get(reverse("collections_app:collections"))
        collection_counts = {
            item.pk: item.records_count
            for item in response.context["collections"]
        }
        self.assertEqual(collection_counts[self.empty.pk], 0)
        response = self.client.get(reverse("collections_app:statistics"))
        counts = {
            item.pk: item.records_count
            for item in response.context["by_collection"]
        }
        self.assertEqual(counts[self.empty.pk], 0)
        response = self.client.get(reverse(
            "collections_app:collection_detail", args=[self.empty.pk],
        ))
        self.assertContains(response, "Коллекция пуста.")

    def test_collection_search_and_query_validation(self):
        response = self.client.get(
            reverse("collections_app:collections"), {"q": "FAVORITES"},
        )
        self.assertEqual(
            [item.pk for item in response.context["collections"]],
            [self.rock.pk],
        )
        response = self.client.get(
            reverse("collections_app:collections"), {"q": "x" * 201},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(list(response.context["collections"]), [])

    def test_collection_pagination_preserves_search(self):
        for index in range(7):
            collection = Collection.objects.create(
                name=f"Test Collection {index}",
            )
            collection.records.add(self.wall)
        response = self.client.get(
            reverse("collections_app:collections"),
            {"q": "Test Collection", "artist": "Pink"},
        )
        parser = LinkParser()
        parser.feed(response.content.decode())
        self.assertEqual(parse_qs(urlsplit(parser.next_url).query), {
            "q": ["Test Collection"], "artist": ["Pink"], "page": ["2"],
        })
        response = self.client.get(
            reverse("collections_app:collections") + parser.next_url,
        )
        self.assertEqual(len(list(response.context["collections"])), 2)

    def test_statistics_aggregate_real_records_and_ignore_unknown_years(self):
        response = self.client.get(reverse("collections_app:statistics"))
        self.assertEqual(response.context["stats"], {
            "total_records": 14, "total_artists": 7,
            "total_collections": 3, "total_users": 2, "total_links": 12,
        })
        year_stats = response.context["year_stats"]
        self.assertEqual(year_stats["oldest_year"], 1959)
        self.assertEqual(year_stats["newest_year"], 2000)
        self.assertEqual(year_stats["known_year_records"], 12)
        known_years = [1969, 1979, 1975, 1959, 2000, *range(1980, 1987)]
        self.assertAlmostEqual(
            year_stats["average_year"], sum(known_years) / 12,
        )
        self.assertEqual({
            item["genre_name"]: item["records_count"]
            for item in response.context["by_genre"]
        }, {"Rock": 9, "Progressive Rock": 2, "Jazz": 1, "Не указан": 2})
        self.assertEqual(response.context["uncollected_count"], 2)
        self.assertEqual(
            {record.pk for record in response.context["uncollected"]},
            {self.unknown.pk, self.no_year.pk},
        )

    def test_statistics_limits_uncollected_preview_to_five_records(self):
        self.rock.records.clear()
        response = self.client.get(reverse("collections_app:statistics"))
        self.assertEqual(response.context["uncollected_count"], 13)
        self.assertEqual(len(response.context["uncollected"]), 5)
        self.assertContains(response, "Показаны первые 5 пластинок")

    def test_empty_database_has_normal_pages_and_zero_statistics(self):
        Record.objects.all().delete()
        Collection.objects.all().delete()
        User.objects.all().delete()
        response = self.catalog()
        self.assertContains(response, "Пластинки не найдены")
        response = self.client.get(reverse("collections_app:statistics"))
        self.assertEqual(response.context["stats"]["total_records"], 0)
        self.assertEqual(response.context["stats"]["total_links"], 0)
        self.assertEqual(response.context["uncollected_count"], 0)
        self.assertIsNone(response.context["year_stats"]["average_year"])
        self.assertEqual(list(response.context["link_rows"]), [])
        self.assertEqual(response.context["page_obj"].paginator.count, 0)
        self.assertContains(response, "В коллекциях пока нет пластинок.")
        self.assertContains(
            response, "Нет пластинок с известным годом выпуска",
        )

    def test_collection_search_handles_cyrillic_case_and_literal_symbols(self):
        russian = Collection.objects.create(name="Классика рока")
        literal = Collection.objects.create(name="Классика [1980].+")
        url = reverse("collections_app:collections")
        response = self.client.get(url, {"q": "классика"})
        self.assertEqual(
            {item.pk for item in response.context["collections"]},
            {russian.pk, literal.pk},
        )
        response = self.client.get(url, {"q": "[1980].+"})
        self.assertEqual(
            [item.pk for item in response.context["collections"]],
            [literal.pk],
        )

    def test_record_search_handles_cyrillic_case_and_literal_symbols(self):
        record = Record.objects.create(
            title="Группа крови [1988].+", artist="Кино", year=1988,
        )
        url = reverse("records:search")
        for query, scope in (
            ("группа", "title"), ("кино", "artist"),
            ("КИНО", "all"), ("крови [1988].+", "all"),
        ):
            with self.subTest(query=query, scope=scope):
                response = self.client.get(url, {"q": query, "scope": scope})
                self.assertEqual(
                    [item.pk for item in response.context["results"]],
                    [record.pk],
                )

    def test_related_artist_filter_preserves_full_sizes_and_unique_rows(self):
        self.jazz_collection.records.add(self.wall, self.wish)
        url = reverse("collections_app:collections")
        response = self.client.get(url, {"artist": "pink"})
        items = list(response.context["collections"])
        self.assertEqual(len(items), 2)
        self.assertEqual(
            {item.pk: item.records_count for item in items},
            {self.rock.pk: 11, self.jazz_collection.pk: 3},
        )
        response = self.client.get(url, {"q": "Rock", "artist": "Pink"})
        self.assertEqual(
            [(item.pk, item.records_count)
             for item in response.context["collections"]],
            [(self.rock.pk, 11)],
        )
        response = self.client.get(url, {"q": "Rock", "artist": "Miles"})
        self.assertEqual(list(response.context["collections"]), [])
        response = self.client.get(url, {"artist": "x" * 201})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_statistics_projects_related_values_and_executes_join_query(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse("collections_app:statistics"))
        rows = list(response.context["link_rows"])
        self.assertEqual(len(rows), 5)
        fields = {
            "id", "collection_id", "record_id", "collection_name",
            "record_title", "record_artist", "record_year",
        }
        for row in rows:
            self.assertIsInstance(row, dict)
            self.assertEqual(set(row), fields)
            link = CollectionRecord.objects.select_related(
                "collection", "record",
            ).get(pk=row["id"])
            self.assertEqual(row, {
                "id": link.pk, "collection_id": link.collection_id,
                "record_id": link.record_id,
                "collection_name": link.collection.name,
                "record_title": link.record.title,
                "record_artist": link.record.artist,
                "record_year": link.record.year,
            })
            self.assertContains(response, reverse(
                "collections_app:collection_detail", args=[link.collection_id],
            ))
            self.assertContains(response, reverse(
                "records:record_detail", args=[link.record_id],
            ))
        projected_queries = [
            item["sql"] for item in queries.captured_queries
            if 'AS "collection_name"' in item["sql"]
            and 'AS "record_title"' in item["sql"]
        ]
        self.assertEqual(len(projected_queries), 1)
        for model in (Collection, Record):
            self.assertIn(
                f'JOIN "{model._meta.db_table}"', projected_queries[0],
            )

    def test_statistics_pagination_makes_every_link_accessible_once(self):
        url = reverse("collections_app:statistics")
        response = self.client.get(url)
        row_ids, page_sizes, row_order = [], [], []
        while True:
            self.assertEqual(response.status_code, 200)
            rows = list(response.context["link_rows"])
            page_sizes.append(len(rows))
            row_ids.extend(row["id"] for row in rows)
            row_order.extend(
                (row["collection_name"], row["record_title"], row["id"])
                for row in rows
            )
            parser = LinkParser()
            parser.feed(response.content.decode())
            if not parser.next_url:
                break
            response = self.client.get(url + parser.next_url)
        self.assertEqual(page_sizes, [5, 5, 2])
        self.assertEqual(len(row_ids), len(set(row_ids)))
        self.assertEqual(set(row_ids), set(
            CollectionRecord.objects.values_list("pk", flat=True),
        ))
        self.assertEqual(row_order, sorted(row_order))
