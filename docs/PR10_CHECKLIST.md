# ПР10 — чек-лист и демонстрация 30 критериев на собственной теме

**Проект:** Vinyl Collection Service (пластинки/коллекции, **не Roomly**). Формулировки Roomly из методички перенесены по правилу из примечания к §7.3 (стр. 175): демонстрация производится на фактических моделях, связях и сценариях своего индивидуального проекта.

**Соответствие предметных областей:** `Room` → `Record` (пластинка); `Booking` → `CollectionRecord` (экземпляр пластинки в коллекции); `Booking.room` → `CollectionRecord.record`; вторую роль связанной сущности выполняет `CollectionRecord.collection`; `users.User` сохранён, но нет несуществующей в исходных данных связи пользователя с отдельной коллекцией. Дата бронирования не переносится: в виниловой предметной области фильтруют по реальному году выпуска, а доступность определяется статусом экземпляра.

**Обозначения:** «Код» — соответствующая реализация присутствует в проекте по инспекции исходников; «Требует запуска» — необходимо подтвердить с установленным Django и/или браузером. `Код` **не означает**, что автоматизированный тест выполнен успешно; фактический протокол — `docs/VERIFICATION_PR10.txt`.

## A. Чек-лист §7.2: 17 требований

| № | Требование по своей теме | Признак выполнения и подтверждение | Статус |
| --- | --- | --- | --- |
| 1 | Admin для пластинок, коллекций, их экземпляров и участников; поиск, связи, сортировка | `records/admin.py`, `collections_app/admin.py`, `users/admin.py`, локализация в `apps.py` | Код; GUI требует запуска |
| 2 | Миграции после новых полей | `records/migrations/0002_*`, `collections_app/migrations/0002_*` | Код; применение `migrate` требуется |
| 3 | Перенос старых включений в статусы `TextChoices` без потерь | `collections_app/migrations/0002_collectionrecord_status.py` → `RunPython` | Код; применение проверить |
| 4 | Свой менеджер QuerySet и повторно используемые состояния | `CollectionRecordQuerySet`, `CollectionRecordManager`; `.current()`, `.available()` в views | Код; тесты требуют запуска |
| 5 | Доступ к рабочим данным через ORM | `records/views.py`, `collections_app/views.py`; старый SQL только для чтения источника ПР7 | Код; SQL-панель требует запуска |
| 6 | Списки с фильтрацией, сортировкой, пагинацией | `/collections/placements/`, `PlacementFilterForm`, `PLACEMENT_SORTS`, `Paginator`, querystring | Код; GUI требует запуска |
| 7 | Доступность экземпляра по состоянию | `IN_COLLECTION` доступен; `RESERVED`/`REMOVED` недоступны, `QuerySet.available()` | Код; тесты требуют запуска |
| 8 | Статистика по трём состояниям | `collections_app/views.py:statistics`, `status_counts`, `Count(filter=Q(...))` | Код; значения проверить после миграции |
| 9 | Страница по slug и `get_absolute_url()` | `records/models.py`, `records/urls.py`, `records/views.py`, миграция данных | Код; HTTP требует запуска |
| 10 | Контекстный процессор с данными для общих шаблонов | `records/context_processors.py`, `vinyl_project/settings.py`, `templates/includes/navigation.html` | Код; HTTP требует запуска |
| 11 | Вычисляемое поле `GeneratedField` | `Record.is_vintage` (год от 1900 до 1990), миграция; SQLite CASE проверен отдельно | Код; Django-проверка требуется |
| 12 | SQL-анализ через Django Debug Toolbar | Настройки PR9 сохраняются, `queryset.query` и `.explain()` в `demo_pr10` | Код; визуальный SQL требует запуска |
| 13 | Проверки через Django Shell | `python manage.py shell` + пример в отчёте; `python manage.py demo_pr10` — воспроизводимая альтернатива | Требует запуска |
| 14 | `python manage.py check` без ошибок | Попытка закончилась `No module named django` | Не подтверждено: установить Django |
| 15 | Автоматизированные тесты выполнены или причины выявлены | `tests/test_pr10.py`, старые тесты; `pytest` не стартует без Django | Причина установлена; выполнение требует запуска |
| 16 | Актуальный README | `README.md`: запуск, модели, статусы, маршруты, SQL, миграции, ограничения | Код/документация подготовлены |
| 17 | Фиксация изменений Git | История `.git`, два PR10-коммита (см. `git log --oneline -n 3`) | Код/коммиты зафиксированы |

## B. Таблица §7.3: 30 критериев для устной защиты

| № | Что показать в Vinyl Collection Service | Где в проекте / пояснение |
| --- | --- | --- |
| 1 | Четыре раздела Django Admin; поиск по названиям, исполнителям, состояниям и связанным коллекциям; сортировку и фильтры | `/admin/`, `records/admin.py`, `collections_app/admin.py`, `users/admin.py`; объяснить `list_display`, `search_fields`, `list_filter`, `ordering` |
| 2 | Состав коллекции внутри её карточки (inline), редактирование состояния экземпляра | `CollectionRecordInline`, `RecordCollectionInline` — `TabularInline`; связи `ForeignKey`, удаление `CASCADE` с осторожностью |
| 3 | Новые поля и миграции | `records/migrations/0002_*`, `collections_app/migrations/0002_*`; `makemigrations --check`, `migrate`, `showmigrations` |
| 4 | Преобразование ранее существовавших записей в статусы без потерь | `RunPython(populate_status)` помечает старые 13 связей как `IN_COLLECTION`; `RESERVED`/`REMOVED` — последующие изменения |
| 5 | Получение и изменение записи через ORM и сохранение | `python manage.py shell`, `Record.objects.first()`, изменение поля `year`, `save`, `refresh_from_db`; можно показать `demo_pr10` |
| 6 | CRUD через ORM для тестовой записи с откатом | `python manage.py demo_pr10` создаёт, сохраняет, обновляет и удаляет объекты внутри отменяемой транзакции |
| 7 | Составные условия `filter()`, `exclude()`, `Q` | `collections_app/views.py:placements()` (`status`, `collection`, `year_from`, `year_to`), `statistics()` |
| 8 | Фильтры по связанным моделям через `__` | `record__year`, `record__title`, `collection__name`, `record__artist`; сравнить с `record_id` |
| 9 | Свой менеджер и цепочки методов QuerySet | `CollectionRecordQuerySet`: `.current()`, `.available()`, `.reserved()`, `.removed()`, `.for_collection()`, `.for_record()`, `.for_year()` |
| 10 | Корректный и некорректный ввод без 500 | `PlacementFilterForm` для года, коллекции, состояния, поиска; `/collections/placements/?year_from=abc` или `?status=unknown`; тест `test_invalid_parameters_do_not_cause_http_500` |
| 11 | Динамическая сортировка с allowlist | `PLACEMENT_SORTS`, `.order_by(*PLACEMENT_SORTS[sort])`; `?sort=-year`, недопустимое значение — ошибка формы |
| 12 | Проекция `values()` необходимых связанных полей | `collections_app/views.py:placements()`, словари `collection_name`, `record_title`, `record_artist`, `record_year` в шаблоне |
| 13 | `annotate()` и `F()` для вычисления связанных значений | `collection_name=F("collection__name")`, `record_title=F("record__title")`, `record_vintage=F("record__is_vintage")` |
| 14 | Подробная страница и 404 отсутствующей записи | `get_object_or_404` в `records/views.py` и `collections_app/views.py`; запрос несуществующего slug / placement ID |
| 15 | Уникальный slug, `reverse()` и `get_absolute_url()` | `records/models.py`, `records/slug_utils.py`, `records/urls.py`, `records/templates/records/includes/record_items.html` |
| 16 | Хранимое вычисляемое поле с изменением исходного значения | `Record.is_vintage` (1900–1990), `db_persist=True`; `record.year=2001; record.save(); record.refresh_from_db()` |
| 17 | Агрегированная статистика по текущим/зарезервированным/выведенным включениям | `statistics()` → `status_counts=CollectionRecord.objects.aggregate(Count(...filter=Q(...)))` |
| 18 | Группировка по коллекциям и жанрам | `by_collection=Collection.objects.annotate(Count(...))`, `by_genre=Record.objects.values("genre_name").annotate(Count(...))` |
| 19 | Оптимизация карточки включения через `select_related` двух моделей | `placement_detail()` → `.select_related("record", "collection")`; Django Debug Toolbar → SQL и JOIN |
| 20 | Реальные SQL запросы реестра с фильтрами и пагинацией | `/collections/placements/?status=in_collection&sort=-year`; Django Debug Toolbar → SQL; различать COUNT и SELECT |
| 21 | Совместная фильтрация/сортировка/пагинация с сохранением GET | `PlacementFilterForm`, `Paginator(PAGE_SIZE=5)`, `templates/includes/pagination.html` с `{% querystring %}` |
| 22 | Доступность винилового экземпляра по реальному статусу вместо даты брони Roomly | `CollectionRecord.objects.available()`; изменить статус в Admin с `IN_COLLECTION` на `RESERVED`, повторить выборку; дата комнаты к винилу неприменима |
| 23 | Контекстный процессор на нескольких страницах | `records/context_processors.py:vinyl_context`, `vinyl_project/settings.py`, `templates/includes/navigation.html`: название и количество пластинок |
| 24 | Enum `TextChoices` в модели и в пользовательской части | `CollectionRecord.Status`, методы QuerySet, шаблонные метки статусов, Admin-действия, статистика |
| 25 | Загрузка связанной информации одним запросом `F()` + `values()` | `placements()`; объяснить, почему `select_related` для словарей не требуется; открыть SQL-панель |
| 26 | Пересчёт значения после изменения исходного года | `GeneratedField is_vintage`, `refresh_from_db`; после года 1969 → 1997 признак меняется с True на False |
| 27 | Именованные маршруты и ссылки в HTML | `records:record_by_slug` и `{{ record.get_absolute_url }}`, старый `records:record_detail` сохранён |
| 28 | Обработка отсутствия и ошибок БД безопасным способом | `get_object_or_404` → 404; транзакционный `import_pr7` ловит `DatabaseError` и отменяет импорт, без порчи базы; тесты `tests/test_import_pr7.py` |
| 29 | Контроль моделей и миграций | `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `showmigrations` — выполнить после `pip install` и `migrate` |
| 30 | Автоматизированный тест поведения | `tests/test_pr10.py`, например `test_statuses_affect_public_lists_and_statistics` или `test_cyrillic_slug_get_absolute_url_and_legacy_route`; `pytest -v` после установки зависимостей |

## C. Подтверждающие скриншоты по §7.4

**Они должны быть сделаны с реально запущенного приложения, а не нарисованы.** После установки зависимостей, `migrate`, `createsuperuser` и запуска сервера подготовьте:

1. `/admin/` — список доменных моделей, русские подписи;
2. `/admin/collections_app/collectionrecord/` — поиск и фильтр по статусу;
3. карточка `Collection` или `Record` в Admin — inline-связи;
4. `/collections/placements/` — форма фильтрации, строка результатов, переход на следующую страницу с сохранением GET;
5. `/collections/statistics/` — показатели по состояниям;
6. редактор с `CollectionRecord.Status` и `CollectionRecordQuerySet` / `Record.is_vintage` и миграциями;
7. SQL вкладка Django Debug Toolbar на странице реестра и карточки экземпляра;
8. терминал после **успешного** `check`, `showmigrations`, `pytest -v`, `git log`.

В среде подготовки сервера с Django не было, поэтому эти изображения не предоставлены; фальшивые скриншоты недопустимы по методичке (§7.4). До выполнения этого пункта и проверки Python-зависимостей нельзя считать проект полностью подтверждённым для сдачи.

## D. Сценарий показа (до 5 минут)

| Время | Показать | Смысл |
| --- | --- | --- |
| 0:00–0:40 | `/admin/` → пластинки, коллекции, реестр экземпляров; фильтр `RESERVED` | `ModelAdmin`, русская локализация, `search_fields`, `TabularInline` |
| 0:40–1:30 | `models.py`, миграции `0002` и `showmigrations` | `TextChoices`, перенос старых данных, миграция `slug`, `GeneratedField` |
| 1:30–2:20 | `/collections/placements/?status=in_collection&sort=-year` и следующая страница | `filter()`, `Q`, `F`, `values`, сортировка, GET и `Paginator` |
| 2:20–3:00 | `mark_reserved` в Admin, обновить реестр и статистику | Реальная доступность коллекционного экземпляра и история |
| 3:00–3:50 | `/records/<slug>/`, `get_absolute_url()`, карточка экземпляра | Постоянные маршруты, 404, `select_related` двух FK |
| 3:50–4:30 | Django Debug Toolbar → SQL | JOIN, COUNT для пагинации, один SELECT для связанных полей |
| 4:30–5:00 | Терминал: `check`, `pytest -v`, `git log --oneline -n 3` | Контроль конфигурации, тесты, два PR10-коммита |

**Пример Django shell без удаления реальных данных:**

```python
from collections_app.models import CollectionRecord
from records.models import Record

print(CollectionRecord.objects.available().count())
print(CollectionRecord.objects.reserved().count())
print(CollectionRecord.objects.for_year(1969).count())
link = CollectionRecord.objects.select_related("collection", "record").first()
if link:
    print(link.collection.name, link.record.title, link.get_status_display())
record = Record.objects.first()
if record:
    print(record.slug, record.get_absolute_url(), record.is_vintage)
```

**Реальный протокол проверок, ошибки зависимостей и команды завершения:** `docs/VERIFICATION_PR10.txt`. **Отчёт по 10 пунктам §7.4:** `docs/REPORT_PR10.md`.
