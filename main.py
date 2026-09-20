"""Главный модуль приложения Vinyl Collection Service."""
from utils import input_int, input_str
from storage import load_records, save_records, load_collections, save_collections
from records import add_record, show_records
from vinyl_collections import (
    add_collection,
    show_collections,
    show_collection_content,
)


def show_main_menu() -> None:
    """Вывести главное меню приложения."""
    print("\n=== Vinyl Collection Service ===")
    print("1. Показать все пластинки")
    print("2. Показать все коллекции")
    print("3. Показать содержимое коллекции")
    print("4. Добавить пластинку")
    print("5. Добавить коллекцию")
    print("6. Найти пластинку")
    print("0. Выход")


def main() -> None:
    """Точка запуска приложения: загрузка данных и главный цикл меню."""
    records = load_records()
    collections = load_collections()

    if not records:
        print("Каталог пластинок пуст. Добавьте первую пластинку.")
    else:
        print(f"Загружено пластинок: {len(records)}")
        print(f"Загружено коллекций: {len(collections)}")

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
            show_collection_content(collections, records, index)

        elif choice == 4:
            title = input_str("Введите название пластинки: ")
            artist = input_str("Введите исполнителя: ")
            genre = input_str("Введите жанр: ")
            year = input_int("Введите год выпуска (0 — если неизвестен): ")
            add_record(records, title, artist, genre, year)
            save_records(records)
            print("Пластинка добавлена.")

        elif choice == 5:
            name = input_str("Введите название коллекции: ")
            if not records:
                print("Сначала добавьте хотя бы одну пластинку.")
                continue

            show_records(records)
            print("Введите номера пластинок по одному. Для завершения введите 0.")
            record_ids = []
            while True:
                num = input_int("Номер пластинки (0 — завершить): ")
                if num == 0:
                    break
                if 1 <= num <= len(records):
                    record_ids.append(records[num - 1]["id"])
                else:
                    print("Пластинки с таким номером нет.")

            add_collection(collections, name, record_ids)
            save_collections(collections)
            print("Коллекция добавлена.")

        elif choice == 6:
            from records import find_record
            query = input_str("Введите название или исполнителя для поиска: ")
            found = find_record(records, query)
            if found:
                print(f"Найдено: {len(found)}")
                for record in found:
                    print(f"  - {record['title']} — {record.get('artist', '?')}")
            else:
                print("Ничего не найдено.")

        elif choice == 0:
            print("Пока!")
            break

        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()