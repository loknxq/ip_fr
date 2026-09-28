from __future__ import annotations


class Record:

    def __init__(
        self,
        record_id: int,
        title: str,
        artist: str = "Неизвестен",
        genre: str = "Не указан",
        year: int = 0,
    ) -> None:
        self.id = record_id
        self.title = title
        self.artist = artist
        self.genre = genre
        self.year = year

    @property
    def display_name(self) -> str:
        year_str = f", {self.year}" if self.year else ""
        return f"{self.title} — {self.artist}{year_str}"

    @staticmethod
    def validate_year(year: int) -> bool:
        from datetime import date
        if year == 0:
            return True
        return 1900 <= year <= date.today().year

    @classmethod
    def from_data(cls, data: dict) -> "Record":
        return cls(
            record_id=data["id"],
            title=data["title"],
            artist=data.get("artist", "Неизвестен"),
            genre=data.get("genre", "Не указан"),
            year=data.get("year", 0),
        )

    def to_data(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "year": self.year,
        }

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"Record(id={self.id}, title={self.title!r})"



def add_record(
    records: list[Record],
    title: str,
    artist: str = "Неизвестен",
    genre: str = "Не указан",
    year: int = 0,
) -> Record:
    new_id = max((r.id for r in records), default=0) + 1
    record = Record(new_id, title, artist, genre, year)
    records.append(record)
    return record


def find_record(records: list[Record], query: str) -> list[Record]:
    query_lower = query.lower()
    return [
        r for r in records
        if query_lower in r.title.lower() or query_lower in r.artist.lower()
    ]


def find_record_by_id(records: list[Record], record_id: int) -> Record | None:
    for record in records:
        if record.id == record_id:
            return record
    return None


def filter_records_by_genre(records: list[Record], genre: str) -> list[Record]:
    genre_lower = genre.lower()
    return [r for r in records if genre_lower in r.genre.lower()]


def sort_records_by_year(records: list[Record]) -> list[Record]:
    return sorted(records, key=lambda r: r.year)


def show_records(records: list[Record]) -> None:
    if not records:
        print("Каталог пластинок пуст.")
        return
    for index, record in enumerate(records, start=1):
        print(f"{index}. {record}")