"""Разовый безопасный перенос ПР7: SQLite (чтение) -> Django ORM."""

import sqlite3
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction

from collections_app.models import Collection, CollectionRecord
from records.models import Record
from users.models import User


SOURCE_QUERIES = {
    "records": (
        "SELECT id, title, artist, genre, year FROM records ORDER BY id"
    ),
    "collections": "SELECT id, name FROM collections ORDER BY id",
    "users": "SELECT id, name, email FROM users ORDER BY id",
    "links": (
        "SELECT collection_id, record_id FROM collection_records "
        "ORDER BY collection_id, record_id"
    ),
}


def read_source(source):
    """SQL нужен только для исходных таблиц, ещё не управляемых Django."""
    if not source.is_file():
        raise CommandError(f"Исходная база не найдена: {source}")
    try:
        with closing(sqlite3.connect(
            source.as_uri() + "?mode=ro", uri=True
        )) as connection:
            connection.row_factory = sqlite3.Row
            return {
                name: [dict(row) for row in connection.execute(query)]
                for name, query in SOURCE_QUERIES.items()
            }
    except (sqlite3.Error, OSError) as error:
        raise CommandError(
            f"Не удалось прочитать структуру базы ПР7: {error}"
        ) from error


def check_identifier(value, label):
    if type(value) is not int or not 0 < value <= 2**63 - 1:
        raise CommandError(f"Некорректный идентификатор {label}: {value!r}")


def validate_rows(model, rows):
    objects = []
    seen = set()
    for row in rows:
        identifier = row["id"]
        label = f"{model.__name__}(id={identifier})"
        check_identifier(identifier, label)
        if identifier in seen:
            raise CommandError(f"Дублирующийся идентификатор: {label}")
        seen.add(identifier)
        for name, value in row.items():
            if name == "id":
                continue
            field = model._meta.get_field(name)
            if value is None and field.null:
                continue
            valid_type = (
                type(value) is int if name == "year"
                else isinstance(value, str)
            )
            if not valid_type:
                raise CommandError(f"Неверный тип поля {label}.{name}")
        obj = model(**row)
        try:
            obj.full_clean(validate_unique=False, validate_constraints=False)
        except ValidationError as error:
            raise CommandError(
                f"Некорректная запись {label}: {error}"
            ) from error
        objects.append(obj)
    return objects


def validate_links(rows, collection_ids, record_ids):
    seen = set()
    for row in rows:
        pair = (row["collection_id"], row["record_id"])
        check_identifier(pair[0], "collection_records.collection_id")
        check_identifier(pair[1], "collection_records.record_id")
        if pair in seen:
            raise CommandError(f"Дублирующаяся связь: {pair}")
        seen.add(pair)
        if pair[0] not in collection_ids or pair[1] not in record_ids:
            raise CommandError(f"Связь с отсутствующим объектом: {pair}")


def save_entities(model, objects):
    created = 0
    for obj in objects:
        current = model.objects.filter(pk=obj.pk).first()
        if current is not None:
            # ПР10: slug формируется при save(), GeneratedField — в SQLite.
            # Они отсутствуют в исходной БД ПР7 и не должны считаться
            # конфликтом при безопасном повторном импорте.
            conflicts = [
                field.name for field in model._meta.concrete_fields
                if not field.generated
                and not (model is Record and field.name == "slug")
                and getattr(current, field.attname)
                != getattr(obj, field.attname)
            ]
            if conflicts:
                raise CommandError(
                    f"Конфликт {model.__name__}(id={obj.pk}): "
                    f"поля {', '.join(conflicts)} отличаются. "
                    "Данные не перезаписаны."
                )
            continue
        obj.save(force_insert=True)
        created += 1
    return created


class Command(BaseCommand):
    help = "Перенести данные ПР7 с сохранением ID и связей без перезаписи."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=str(settings.BASE_DIR / "data" / "vinyl.sqlite"),
            help="Путь к исходной SQLite-базе ПР7 (только чтение).",
        )
        parser.add_argument(
            "--check-only",
            action="store_true",
            help="Проверить полный перенос и откатить изменения в конце.",
        )

    def handle(self, *args, **options):
        source = Path(options["source"]).expanduser().resolve()
        target = Path(settings.DATABASES["default"]["NAME"]).resolve()
        if source == target:
            raise CommandError("Исходная и целевая базы должны различаться.")
        data = read_source(source)
        records = validate_rows(Record, data["records"])
        users = validate_rows(User, data["users"])
        collections = validate_rows(Collection, data["collections"])
        validate_links(
            data["links"],
            {obj.pk for obj in collections},
            {obj.pk for obj in records},
        )
        try:
            with transaction.atomic():
                counts = {
                    "пластинок": save_entities(Record, records),
                    "пользователей": save_entities(User, users),
                    "коллекций": save_entities(Collection, collections),
                    "связей": 0,
                }
                for row in data["links"]:
                    link = CollectionRecord(**row)
                    link.full_clean(
                        validate_unique=False, validate_constraints=False
                    )
                    _, created = CollectionRecord.objects.get_or_create(**row)
                    counts["связей"] += int(created)
                if options["check_only"]:
                    transaction.set_rollback(True)
        except (DatabaseError, ValidationError) as error:
            raise CommandError(
                f"Перенос отменён целиком: {error}"
            ) from error
        action = (
            "Проверка завершена, изменения отменены. Было бы добавлено"
            if options["check_only"] else "Импорт завершён. Добавлено"
        )
        details = ", ".join(
            f"{name}: {count}" for name, count in counts.items()
        )
        self.stdout.write(self.style.SUCCESS(f"{action}: {details}."))
