from __future__ import annotations

from utils import input_int, input_str
from storage import (
    load_records, save_records,
    load_collections, save_collections,
    load_users, save_users,
)
from models import Record, Collection, User
from models.records import add_record, show_records, find_record
from models.collections import (
    add_collection,
    show_collections,
    show_collection_content,
    find_collection_by_id,
)
from models.users import add_user, show_users, find_user


def show_main_menu() -> None:
    print("\n=== Vinyl Collection Service ===")
    print("1. Показать все пластинки")
    print("2. Показать все коллекции")
    print("3. Показать содержимое коллекции")
    print("4. Добавить пластинку")
    print("5. Добавить коллекцию")
    print("6. Найти пластинку")
    print("7. Показать пользователей")
    print("8. Добавить пользователя")
    print("0. Выход")


def create_new_collection(
    collections: list[Collection],
    records: list[Record],
) -> None:
    """Создать новую коллекцию с выбором пластинок из каталога."""
    name = input_str("Введите название коллекции: ")
    if not records:
        print("Сначала добавьте хотя бы одну пластинку.")
        return

    show_records(records)
    print("Введите номера пластинок по одному. Для завершения введите 0.")

    selected: list[Record] = []
    while True:
        num = input_int("Номер пластинки (0 — завершить): ")
        if num == 0:
            break
        if 1 <= num <= len(records):
            selected.append(records[num - 1])
        else:
            print("Пластинки с таким номером нет.")

    collection = add_collection(collections, name, selected)
    print(f"Коллекция создана: {collection}")


def main() -> None:
    """Точка запуска: загрузка данных в виде объектов и главный цикл меню."""
    records = load_records()
    collections = load_collections(records)
    users = load_users()

    print(f"Загружено пластинок: {len(records)}")
    print(f"Загружено коллекций: {len(collections)}")
    print(f"Загружено пользователей: {len(users)}")

    while True:
        show_main_menu()
        choice = input_int("Выберите действие: ")

        if choice == 1:
            show_records(records)

        elif choice == 2:
            show_collections(collections)

        elif choice == 3:
            if not collections:
                print("Коллекции отсутствуют.")
                continue
            show_collections(collections)
            index = input_int("Введите номер коллекции: ")
            if 1 <= index <= len(collections):
                show_collection_content(collections[index - 1])
            else:
                print("Коллекции с таким номером нет.")

        elif choice == 4:
            title = input_str("Введите название пластинки: ")
            artist = input_str("Введите исполнителя: ")
            genre = input_str("Введите жанр: ")
            year = input_int("Введите год выпуска (0 — если неизвестен): ")
            if not Record.validate_year(year):
                print("Некорректный год. Пластинка не добавлена.")
                continue
            record = add_record(records, title, artist, genre, year)
            save_records(records)
            print(f"Пластинка добавлена: {record}")

        elif choice == 5:
            create_new_collection(collections, records)
            save_collections(collections)

        elif choice == 6:
            query = input_str("Введите название или исполнителя для поиска: ")
            found = find_record(records, query)
            if found:
                print(f"Найдено: {len(found)}")
                for record in found:
                    print(f"  - {record}")
            else:
                print("Ничего не найдено.")

        elif choice == 7:
            show_users(users)

        elif choice == 8:
            name = input_str("Введите имя пользователя: ")
            email = input_str("Введите email: ")
            user = add_user(users, name, email)
            save_users(users)
            print(f"Пользователь добавлен: {user}")

        elif choice == 0:
            print("Пока!")
            break

        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()