"""Модуль для работы с коллекциями пластинок."""


def add_collection(collections: list[dict], name: str, record_ids: list[int]) -> None:
    """Добавить новую коллекцию в список collections.

    Каждая коллекция представлена словарём с полями:
    id, name, record_ids.
    """
    new_id = len(collections) + 1
    collections.append({
        "id": new_id,
        "name": name,
        "record_ids": record_ids,
    })


def show_collections(collections: list[dict]) -> None:
    """Вывести список всех коллекций."""
    if not collections:
        print("Коллекции отсутствуют.")
        return
    for index, collection in enumerate(collections, start=1):
        print(f"{index}. {collection['name']} (id={collection['id']})")


def show_collection_content(collections: list[dict], records: list[dict],
                            collection_index: int) -> None:
    """Вывести содержимое коллекции по её порядковому номеру.

    collection_index — номер коллекции в списке (начиная с 1).
    """
    if collection_index < 1 or collection_index > len(collections):
        print("Коллекция с таким номером не найдена.")
        return

    collection = collections[collection_index - 1]
    record_ids = collection["record_ids"]

    if not record_ids:
        print(f"Коллекция «{collection['name']}» пуста.")
        return

    print(f"Содержимое коллекции «{collection['name']}»:")
    for record_id in record_ids:
        title = get_record_title_by_id(records, record_id)
        if title:
            print(f"  - {title}")
        else:
            print(f"  - Пластинка с id={record_id} не найдена")


def get_record_title_by_id(records: list[dict], record_id: int) -> str | None:
    """Вспомогательная функция: вернуть название пластинки по id."""
    for record in records:
        if record["id"] == record_id:
            return record["title"]
    return None