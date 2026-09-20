"""Модуль для работы с коллекциями: класс Collection и функции обработки."""
from __future__ import annotations
from .records import Record


class Collection:
    """Коллекция виниловых пластинок."""

    def __init__(
        self,
        collection_id: int,
        name: str,
        records: list[Record] | None = None,
    ) -> None:
        """Создать объект коллекции.

        records — список объектов Record, входящих в коллекцию.
        """
        self.id = collection_id
        self.name = name
        self.records: list[Record] = records if records is not None else []

    @property
    def size(self) -> int:
        """Количество пластинок в коллекции."""
        return len(self.records)

    def add_record(self, record: Record) -> None:
        """Добавить пластинку в коллекцию (если её там ещё нет)."""
        if record not in self.records:
            self.records.append(record)

    def remove_record(self, record: Record) -> bool:
        """Удалить пластинку из коллекции. Возвращает True, если удаление выполнено."""
        if record in self.records:
            self.records.remove(record)
            return True
        return False

    @classmethod
    def from_data(cls, data: dict, all_records: list[Record]) -> "Collection":
        """Создать объект Collection из словаря.

        all_records — общий каталог пластинок для восстановления связей по id.
        """
        collection = cls(
            collection_id=data["id"],
            name=data["name"],
        )
        for record_id in data.get("record_ids", []):
            for record in all_records:
                if record.id == record_id:
                    collection.add_record(record)
                    break
        return collection

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON.

        Хранятся только id пластинок — это требование ПР3.
        """
        return {
            "id": self.id,
            "name": self.name,
            "record_ids": [r.id for r in self.records],
        }

    def __str__(self) -> str:
        """Строковое представление коллекции."""
        return f"Коллекция «{self.name}» ({self.size} шт.)"

    def __repr__(self) -> str:
        return f"Collection(id={self.id}, name={self.name!r})"


# ---------- Функции обработки коллекции коллекций ----------

def add_collection(
    collections: list[Collection],
    name: str,
    records: list[Record] | None = None,
) -> Collection:
    """Создать объект Collection и добавить его в коллекцию.

    Возвращает созданный объект.
    """
    new_id = max((c.id for c in collections), default=0) + 1
    collection = Collection(new_id, name, records or [])
    collections.append(collection)
    return collection


def find_collection_by_id(
    collections: list[Collection], collection_id: int
) -> Collection | None:
    """Найти коллекцию по её id."""
    for collection in collections:
        if collection.id == collection_id:
            return collection
    return None


def show_collections(collections: list[Collection]) -> None:
    """Вывести список всех коллекций."""
    if not collections:
        print("Коллекции отсутствуют.")
        return
    for index, collection in enumerate(collections, start=1):
        print(f"{index}. {collection}")


def show_collection_content(collection: Collection) -> None:
    """Вывести содержимое одной коллекции."""
    if not collection.records:
        print(f"Коллекция «{collection.name}» пуста.")
        return
    print(f"Содержимое коллекции «{collection.name}»:")
    for record in collection.records:
        print(f"  - {record}")