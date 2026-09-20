"""Тесты для модуля records."""
from records import add_record, find_record, get_record_title


def test_add_record():
    records = []
    add_record(records, "Abbey Road", "The Beatles", "Rock", 1969)
    assert len(records) == 1
    assert records[0]["title"] == "Abbey Road"
    assert records[0]["artist"] == "The Beatles"
    assert records[0]["year"] == 1969


def test_find_record_by_title():
    records = []
    add_record(records, "Abbey Road", "The Beatles")
    add_record(records, "The Dark Side of the Moon", "Pink Floyd")
    found = find_record(records, "road")
    assert len(found) == 1
    assert found[0]["title"] == "Abbey Road"


def test_find_record_by_artist():
    records = []
    add_record(records, "Abbey Road", "The Beatles")
    add_record(records, "The Dark Side of the Moon", "Pink Floyd")
    found = find_record(records, "pink")
    assert len(found) == 1
    assert found[0]["artist"] == "Pink Floyd"


def test_get_record_title():
    records = []
    add_record(records, "Abbey Road", "The Beatles")
    assert get_record_title(records, 1) == "Abbey Road"
    assert get_record_title(records, 99) is None