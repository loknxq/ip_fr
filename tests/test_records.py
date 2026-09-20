"""Тесты для класса Record и функций модуля records."""
from models import Record
from models.records import (
    add_record, find_record, find_record_by_id,
    filter_records_by_genre, sort_records_by_year,
)


def test_record_creation():
    record = Record(1, "Abbey Road", "The Beatles", "Rock", 1969)
    assert record.id == 1
    assert record.title == "Abbey Road"
    assert record.artist == "The Beatles"
    assert record.year == 1969


def test_record_str():
    record = Record(1, "Abbey Road", "The Beatles", "Rock", 1969)
    assert "Abbey Road" in str(record)
    assert "The Beatles" in str(record)


def test_record_validate_year():
    assert Record.validate_year(0)
    assert Record.validate_year(1969)
    assert not Record.validate_year(1800)


def test_record_from_data():
    data = {"id": 1, "title": "Abbey Road", "artist": "The Beatles", "year": 1969}
    record = Record.from_data(data)
    assert record.title == "Abbey Road"
    assert record.artist == "The Beatles"


def test_add_record():
    records = []
    record = add_record(records, "Abbey Road", "The Beatles", "Rock", 1969)
    assert len(records) == 1
    assert isinstance(record, Record)
    assert record.id == 1


def test_find_record_by_title():
    records = []
    add_record(records, "Abbey Road", "The Beatles")
    add_record(records, "The Wall", "Pink Floyd")
    found = find_record(records, "road")
    assert len(found) == 1
    assert found[0].title == "Abbey Road"


def test_find_record_by_artist():
    records = []
    add_record(records, "Abbey Road", "The Beatles")
    add_record(records, "The Wall", "Pink Floyd")
    found = find_record(records, "pink")
    assert len(found) == 1
    assert found[0].artist == "Pink Floyd"


def test_find_record_by_id():
    records = [Record(1, "Abbey Road")]
    assert find_record_by_id(records, 1).title == "Abbey Road"
    assert find_record_by_id(records, 99) is None


def test_filter_records_by_genre():
    records = [
        Record(1, "Abbey Road", "The Beatles", "Rock"),
        Record(2, "The Wall", "Pink Floyd", "Progressive Rock"),
    ]
    found = filter_records_by_genre(records, "rock")
    assert len(found) == 2


def test_sort_records_by_year():
    records = [
        Record(1, "A", year=2000),
        Record(2, "B", year=1980),
        Record(3, "C", year=1990),
    ]
    sorted_records = sort_records_by_year(records)
    assert [r.year for r in sorted_records] == [1980, 1990, 2000]