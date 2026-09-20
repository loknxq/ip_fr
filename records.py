"""Модуль для работы с каталогом пластинок."""


def add_record(
    records: list[dict],
    title: str,
    artist: str = "Неизвестен",
    genre: str = "Не указан",
    year: int = 0,
) -> None:
    """Добавить новую пластинку в список records.

    Каждая пластинка представлена словарём с полями:
    id, title, artist, genre, year.
    """
    new_id = len(records) + 1
    records.append({
        "id": new_id,
        "title": title,
        "artist": artist,
        "genre": genre,
        "year": year,
    })


def find_record(records: list[dict], query: str) -> list[dict]:
    """Найти пластинки по подстроке в названии или исполнителе.

    Возвращает список найденных пластинок.
    """
    query_lower = query.lower()
    return [
        record for record in records
        if query_lower in record["title"].lower()
        or query_lower in record.get("artist", "").lower()
    ]


def get_record_title(records: list[dict], record_id: int) -> str | None:
    """Вернуть название пластинки по её id.

    Если пластинка не найдена, возвращает None.
    """
    for record in records:
        if record["id"] == record_id:
            return record["title"]
    return None


def show_records(records: list[dict]) -> None:
    """Вывести список всех пластинок в виде нумерованного списка.

    Формат: «N. Название — Исполнитель (год)».
    """
    if not records:
        print("Каталог пластинок пуст.")
        return
    for index, record in enumerate(records, start=1):
        artist = record.get("artist", "Неизвестен")
        year = record.get("year", 0)
        year_str = f", {year}" if year else ""
        print(f"{index}. {record['title']} — {artist}{year_str} (id={record['id']})")