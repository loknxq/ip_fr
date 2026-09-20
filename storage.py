"""Модуль для сохранения и загрузки данных проекта в JSON-файлы."""
import json
import os

DATA_DIR = "data"
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
COLLECTIONS_FILE = os.path.join(DATA_DIR, "collections.json")


def load_records() -> list[dict]:
    """Загрузить список пластинок из JSON-файла.

    Если файл отсутствует или повреждён, возвращает пустой список.
    """
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Ошибка: файл данных пластинок повреждён. Будет создан новый.")
        return []


def save_records(records: list[dict]) -> None:
    """Сохранить список пластинок в JSON-файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RECORDS_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def load_collections() -> list[dict]:
    """Загрузить список коллекций из JSON-файла.

    Если файл отсутствует или повреждён, возвращает пустой список.
    """
    try:
        with open(COLLECTIONS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Ошибка: файл данных коллекций повреждён. Будет создан новый.")
        return []


def save_collections(collections: list[dict]) -> None:
    """Сохранить список коллекций в JSON-файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(COLLECTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(collections, file, ensure_ascii=False, indent=2)