from __future__ import annotations
import json
import os

from models import Record, Collection, User

DATA_DIR = "data"
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
COLLECTIONS_FILE = os.path.join(DATA_DIR, "collections.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def load_records() -> list[Record]:
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return [Record.from_data(item) for item in data]
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, KeyError):
        print("Ошибка: файл данных пластинок повреждён. Будет создан новый.")
        return []


def save_records(records: list[Record]) -> None:
    _ensure_data_dir()
    with open(RECORDS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            [r.to_data() for r in records],
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_collections(all_records: list[Record]) -> list[Collection]:
    try:
        with open(COLLECTIONS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return [Collection.from_data(item, all_records) for item in data]
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, KeyError):
        print("Ошибка: файл данных коллекций повреждён. Будет создан новый.")
        return []


def save_collections(collections: list[Collection]) -> None:
    _ensure_data_dir()
    with open(COLLECTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            [c.to_data() for c in collections],
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_users() -> list[User]:
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return [User.from_data(item) for item in data]
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, KeyError):
        print("Ошибка: файл данных пользователей повреждён. Будет создан новый.")
        return []


def save_users(users: list[User]) -> None:
    _ensure_data_dir()
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            [u.to_data() for u in users],
            file,
            ensure_ascii=False,
            indent=2,
        )
