"""Тесты для модуля collections."""
from vinyl_collections import add_collection, get_record_title_by_id


def test_add_collection():
    collections = []
    add_collection(collections, "The Beatles", [1, 2])
    assert len(collections) == 1
    assert collections[0]["name"] == "The Beatles"
    assert collections[0]["record_ids"] == [1, 2]


def test_get_record_title_by_id():
    records = [{"id": 1, "title": "Abbey Road"}]
    assert get_record_title_by_id(records, 1) == "Abbey Road"
    assert get_record_title_by_id(records, 2) is None