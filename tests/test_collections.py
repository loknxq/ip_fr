"""Тесты для класса Collection."""
from models import Record, Collection
from models.collections import add_collection, find_collection_by_id


def test_collection_creation():
    collection = Collection(1, "Классика рока")
    assert collection.id == 1
    assert collection.name == "Классика рока"
    assert collection.size == 0


def test_collection_add_record():
    record = Record(1, "Abbey Road", "The Beatles")
    collection = Collection(1, "Классика рока")
    collection.add_record(record)
    assert collection.size == 1
    assert record in collection.records


def test_collection_add_duplicate():
    record = Record(1, "Abbey Road", "The Beatles")
    collection = Collection(1, "Классика рока")
    collection.add_record(record)
    collection.add_record(record)
    assert collection.size == 1


def test_collection_remove_record():
    record = Record(1, "Abbey Road", "The Beatles")
    collection = Collection(1, "Классика рока", [record])
    assert collection.remove_record(record) is True
    assert collection.size == 0


def test_collection_str():
    collection = Collection(1, "Классика рока", [Record(1, "A")])
    assert "Классика рока" in str(collection)
    assert "1" in str(collection)


def test_collection_to_data():
    record = Record(1, "Abbey Road", "The Beatles")
    collection = Collection(1, "Классика рока", [record])
    data = collection.to_data()
    assert data["id"] == 1
    assert data["name"] == "Классика рока"
    assert data["record_ids"] == [1]


def test_add_collection():
    collections = []
    collection = add_collection(collections, "Новая коллекция")
    assert len(collections) == 1
    assert isinstance(collection, Collection)


def test_find_collection_by_id():
    collections = [Collection(1, "A"), Collection(2, "B")]
    assert find_collection_by_id(collections, 2).name == "B"
    assert find_collection_by_id(collections, 99) is None