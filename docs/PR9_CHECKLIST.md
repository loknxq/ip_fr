# ПР9: соответствие требованиям индивидуального проекта

Документ сопоставляет результат доработки Vinyl Collection Service с 31 пунктом
чек-листа §7.2 практической работы №9 «Модели Django, связи и операции с базой
данных через ORM». Требования примера Roomly адаптированы к пластинкам,
коллекциям, пользователям и составу коллекций.

## Подтверждённые результаты проверки

Проверки выполнены 15 ноября 2026 года:

| Проверка | Фактический результат |
| --- | --- |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check` | `No changes detected` |
| `python manage.py showmigrations` | Все существующие миграции отмечены `[X]`, включая `records.0001_initial`, `users.0001_initial`, `collections_app.0001_initial` |
| `pytest -v` | **76 passed, 44 subtests passed** |
| `flake8 . --extend-exclude=venv` | Замечаний нет; завершение с кодом `0` |
| Перенос ПР7 | **10 пластинок, 5 коллекций, 2 пользователя, 13 связей**; сохранены исходные идентификаторы, значения полей и пары связей |

Представления, маршруты, контекст и сформированный HTML проверены через
**Django Test Client**. Полноценная ручная проверка в браузере не выполнена:
ограничения среды запрещают Chromium необходимые операции с сокетами, а
доступный облачный браузер работает в другом окружении и не видит локальный
сервер проекта. Визуальная браузерная проверка и браузерные скриншоты в состав
подтверждений не включены.

## Где находятся проверки

В таблице используются сокращения с однозначным соответствием файлу и классу:

| Обозначение | Файл и класс |
| --- | --- |
| `M` | `tests/test_orm_models.py::ModelTests` |
| `V` | `tests/test_orm_views.py::ORMViewTests` |
| `I` | `tests/test_import_pr7.py::ImportTests` |
| `D` | `tests/test_demo_orm.py::DemoOrmTests` |

Например, `V.test_missing_objects_return_404` означает метод
`test_missing_objects_return_404` класса `ORMViewTests` в
`tests/test_orm_views.py`. Его можно запустить отдельно:

```bash
pytest tests/test_orm_views.py::ORMViewTests::test_missing_objects_return_404 -v
```

## Чек-лист §7.2: 31 пункт

| № | Требование | Реализация в проекте | Подтверждение |
| --- | --- | --- | --- |
| 1 | Существующий проект сохранён и продолжен | Сохранены `vinyl_project/`, `homepage/`, `records/`, `collections_app/`, маршруты и шаблоны. Сохранены `main.py`, `models/`, `storage.py` и JSON-данные консольной версии предыдущих работ | `V.test_previous_pages_are_available`; прежние тесты `tests/test_records.py`, `tests/test_collections.py`, `tests/test_users.py` |
| 2 | Определены сущности и соответствующие модели Django | `Record` в `records/models.py`, `User` в `users/models.py`, `Collection` и `CollectionRecord` в `collections_app/models.py` | Просмотр моделей; `M.test_string_representations_are_readable`; `I.test_preserves_ids_values_links_and_source_bytes` |
| 3 | Полям назначены подходящие типы | `CharField`, `EmailField`, `PositiveIntegerField`, `ForeignKey`, `ManyToManyField`; определения находятся в трёх файлах моделей | `M.test_unknown_year_and_genre_are_supported`; `M.test_invalid_year_is_rejected`; `M.test_required_fields_and_email_are_validated` |
| 4 | Заданы обязательность, значения по умолчанию и ограничения | Обязательные названия/имена, ограничение длины, `year=0` для неизвестного года, поддержка исходных `NULL`, проверка года, уникальность пары коллекция–пластинка | `M.test_duplicate_pair_is_rejected_by_database`; `M.test_unknown_year_and_genre_are_supported`; `M.test_required_fields_and_email_are_validated` |
| 5 | Определены первичные ключи | Автоматические `BigAutoField` во всех моделях; исходные ID основных сущностей сохраняются при импорте | Три файла `0001_initial.py`; `I.test_preserves_ids_values_links_and_source_bytes` |
| 6 | Реализованы связи средствами ORM | `Collection.records` через `CollectionRecord`; два внешних ключа `collection` и `record` | `collections_app/models.py`; `M.test_forward_and_reverse_relations` |
| 7 | Настроены `on_delete` и `related_name` | `CASCADE` удаляет записи состава при удалении коллекции/пластинки; обратные имена `collections`, `record_links`, `collection_links` | `M.test_collection_deletion_removes_only_links`; `M.test_record_deletion_preserves_collection` |
| 8 | Созданы миграции | `records/migrations/0001_initial.py`, `users/migrations/0001_initial.py`, `collections_app/migrations/0001_initial.py` | `makemigrations --check`: `No changes detected`; миграции создают таблицы и ограничения |
| 9 | Миграции применены к нужной базе | `vinyl_project/settings.py`: Django использует `BASE_DIR / "db.sqlite3"`; исходная `data/vinyl.sqlite` используется только как источник переноса | `showmigrations`: `[X]` у всех миграций; успешный перенос `10 / 5 / 2 / 13` |
| 10 | Проверены прямые и обратные связи | `link.collection`, `link.record`, `collection.records`, `record.collections`, `record_links`, `collection_links` | `M.test_forward_and_reverse_relations`; `demo_orm` |
| 11 | Реализовано получение наборов объектов | `Record.objects.all()` в `records/views.py::_catalog_context`; аннотированный список коллекций в `collections_app/views.py::collections` | `V.test_catalog_is_ordered_and_has_five_items_per_page`; `V.test_previous_pages_are_available` |
| 12 | Реализовано получение одного объекта | `get_object_or_404()` в обеих карточках; `objects.get()` в `demo_orm` и тестах | `V.test_details_and_related_objects_need_two_queries`; `V.test_missing_objects_return_404`; `M.test_crud_and_get_missing_multiple_objects` |
| 13 | Реализованы создание, изменение и удаление | Все модели зарегистрированы в `admin.py`; команда `collections_app/management/commands/demo_orm.py` показывает `create()`, `get()`, `save()`, `delete()` с обязательным откатом | `M.test_crud_and_get_missing_multiple_objects`; `M.test_user_create_save_read_and_delete`; `M.test_collection_crud_and_membership_changes`; оба теста `D` |
| 14 | Реализована фильтрация по одному условию | Фильтр `genre=...` в `records/views.py::_catalog_context` | `V.test_single_filter_and_year_range` |
| 15 | Реализована фильтрация по нескольким условиям | Одновременные `year__gte` и `year__lte`; совместная работа поиска, жанра, диапазона, коллекции и известности года | `V.test_single_filter_and_year_range`; `V.test_search_filters_and_sort_survive_page_transition` |
| 16 | Реализована фильтрация по полю связанной модели | `records__artist__iregex` в `collections_app/views.py::collections`; пользователь ищет коллекции с пластинками указанного исполнителя | `V.test_related_artist_filter_preserves_full_sizes_and_unique_rows` проверяет результат, отсутствие дублей и полный размер коллекции |
| 17 | Реализован `exclude()` | Исключение `year=0` и `year IS NULL` из каталога по параметру `known_year=1` и из статистики годов | `V.test_exclude_unknown_years`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years` |
| 18 | Реализован поиск по строковому полю | Поиск по `title` при `scope=title`; поиск коллекции по `name`. Для кириллицы применяется экранированный `iregex` | `V.test_search_uses_title_or_artist_and_scopes`; `V.test_collection_search_handles_cyrillic_case_and_literal_symbols`; `V.test_record_search_handles_cyrillic_case_and_literal_symbols` |
| 19 | Реализован поиск по нескольким полям | В каталоге и поиске `Q(title...) OR Q(artist...)` при `scope=all` | `records/views.py::_catalog_context`; `V.test_search_uses_title_or_artist_and_scopes`; `V.test_record_search_handles_cyrillic_case_and_literal_symbols` |
| 20 | Реализована сортировка | `RECORD_SORTS` в `records/forms.py`; варианты по названию, исполнителю и году; состав коллекции сортируется по `record__title` | `V.test_catalog_is_ordered_and_has_five_items_per_page`; `V.test_sort_by_several_fields`; `V.test_reverse_year_sort_and_one_sided_ranges` |
| 21 | Реализована оптимизированная выборка связанных данных | `prefetch_related("collections")` в карточке пластинки; `select_related("record")` в составе коллекции | `V.test_details_and_related_objects_need_two_queries`; `M.test_select_related_loads_both_foreign_keys_in_one_query` |
| 22 | Получается сокращённый набор полей | `values_list("genre", flat=True).distinct()` для вариантов жанра; `values("genre_name")` для группировки статистики | `records/forms.py::RecordFilterForm.__init__`; `collections_app/views.py::statistics`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years` |
| 23 | Реализовано агрегирование | `aggregate()` с `Count`, `Min`, `Max`, `Avg` в `collections_app/views.py::statistics` | `V.test_statistics_aggregate_real_records_and_ignore_unknown_years`; `V.test_empty_database_has_normal_pages_and_zero_statistics` |
| 24 | Реализованы аннотации и группировка | `Count("records", distinct=True)` у списка коллекций; аннотации по коллекциям и жанрам в статистике | `V.test_related_artist_filter_preserves_full_sizes_and_unique_rows`; `V.test_empty_collections_remain_in_lists_statistics_and_details`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years` |
| 25 | Реализован постраничный вывод | `Paginator(..., PAGE_SIZE)` с размером страницы `5` в каталоге и списке коллекций; `get_page()` обрабатывает номер страницы | `V.test_catalog_is_ordered_and_has_five_items_per_page`; `V.test_invalid_page_numbers_use_safe_first_or_last_page` |
| 26 | Навигация сохраняет поиск, фильтры и сортировку | `templates/includes/pagination.html`: `{% querystring page=... %}`; формы не передают старый параметр `page` | `V.test_search_filters_and_sort_survive_page_transition`; `V.test_collection_pagination_preserves_search` |
| 27 | ORM интегрирован в представления и шаблоны | `records/views.py`, `collections_app/views.py`; контекст поступает в существующие шаблоны соответствующих приложений | `V.test_previous_pages_are_available`; `V.test_details_and_related_objects_need_two_queries`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years` |
| 28 | Обработаны отсутствие объектов, пустые результаты и неправильный ввод | Формы в `records/forms.py`, `collections_app/forms.py`; `get_object_or_404()`; пустые состояния шаблонов; разрешённый словарь сортировки | `V.test_missing_objects_return_404`; `V.test_invalid_filter_parameters_show_errors_without_server_error`; `V.test_empty_database_has_normal_pages_and_zero_statistics`; `V.test_empty_search_and_sql_metacharacters_are_literal` |
| 29 | Проверены модели, связи, миграции, запросы и сценарии | Тесты `M`, `V`, `I`, `D`; сохранены прежние ООП-тесты; выполнены команды проверки | `76 passed, 44 subtests passed`; `check`: `0` замечаний; все миграции `[X]`; `makemigrations --check`: изменений нет; `flake8`: замечаний нет |
| 30 | Актуализирован README; изменения фиксируются коммитами `PR9:` | `README.md`: модели, запуск, импорт и проверки; исходное состояние сохранено коммитом `f740e0b` с меткой `PR9:`; финальные коммиты проверяются в комплектном репозитории | `git log --oneline --grep="^PR9:"`; содержимое `README.md` и файлов `docs/` |
| 31 | Не менее 15 разных ORM-выражений с минимумами по категориям | [Реестр ORM-запросов](ORM_QUERIES.md) содержит 15 завершённых выборок, используемых страницами и формами | Подсчёт не включает импортер, `demo_orm`, тестовые запросы и отдельные промежуточные вызовы цепочки каталога; соответствие категориям приведено в реестре |

## Сохранность данных и границы предметной области

Исходная база ПР7 содержит независимых пользователей и связь многие-ко-многим
между коллекциями и пластинками. Связь пользователя с коллекцией в
источнике отсутствует; вымышленные владельцы при переносе не назначаются.
`users.User` представляет участника предметной области и не заменяет
`django.contrib.auth.models.User`, который используется для входа в админку.

Команда `import_pr7` читает исходную SQLite-базу в режиме `mode=ro`, проверяет
ID, типы и связи, затем пишет в целевую базу через ORM внутри транзакции.
Повторный импорт идентичных данных не создаёт дублей; конфликт вызывает полный
откат. Проверки: `I.test_preserves_ids_values_links_and_source_bytes`,
`I.test_identical_repeat_import_does_not_duplicate`,
`I.test_conflict_rolls_back_preceding_inserts`,
`I.test_dangling_relation_rolls_back`.

Старые файлы SQL и JSON-версии сохранены как результаты предыдущих практических.
В действующих Django-представлениях прямые SQL-запросы отсутствуют. SQL в
`import_pr7` используется только для чтения прежних таблиц, которыми Django
не управляет.

## Сценарий защиты: до пяти минут

Это план демонстрации студентом на своём компьютере. Перед защитой выполните
установку, миграции и импорт по `README.md`, создайте локального администратора
командой `python manage.py createsuperuser` и запустите
`python manage.py runserver`. Фактическая ручная демонстрация в браузере ещё
не заявлена как выполненная.

| Время | Что показать | Что объяснить |
| --- | --- | --- |
| 0:00–0:45 | Три файла моделей и `collections_app/migrations/0001_initial.py` | Четыре модели; M2M через два `ForeignKey`; первичные ключи, уникальная пара, `CASCADE`, обратные имена |
| 0:45–1:15 | `python manage.py check`, `python manage.py showmigrations` | Настройки без ошибок; все миграции применены к `db.sqlite3`; исходная база сохранена |
| 1:15–2:00 | `/records/?year_from=1950&year_to=2000&known_year=1&sort=-year`; переход на вторую страницу | Фильтрация выполняется до сортировки и пагинации; сохраняются все параметры. Затем `year_from=abc` показывает ошибку формы |
| 2:00–2:45 | `/collections/?artist=Pink`, затем `/collections/?q=классика`; карточки `/records/1/` и `/collections/1/` | Фильтр по полю связанной модели; Unicode-поиск; полный размер коллекций; `select_related` и `prefetch_related` |
| 2:45–3:15 | `/collections/statistics/` | Исходные итоги `10 / 5 / 2 / 13`; агрегирование, группировка, исключение неизвестного года, пластинки вне коллекций |
| 3:15–4:00 | `python manage.py demo_orm` | Реальные `create/get/save/delete`, изменение внешнего ключа, обязательный откат временной транзакции |
| 4:00–5:00 | Следующий пример Django shell и `/admin/` | Прямые/обратные связи; зарегистрированные модели и формы редактирования; итоговые проверки и `git log --oneline --grep="^PR9:"` |

Пример для `python manage.py shell` после импорта исходных данных:

```python
from collections_app.models import CollectionRecord

link = CollectionRecord.objects.select_related("collection", "record").first()
print(link.collection.name, link.record.title)
print(list(link.collection.records.values_list("title", flat=True)))
print(list(link.record.collections.values_list("name", flat=True)))
```

## Сведения, которые студент должен подтвердить отдельно

- **Прохождение Яндекс Практикума не подтверждено.** Чек-лист §7.1 необходимо
  заполнять по фактическим результатам своего аккаунта. Наличие реализации ORM
  в этом проекте не подтверждает прохождение учебных заданий на платформе.
- **Реквизиты студента не подтверждены.** Организацию, ФИО, учебную группу и
  номер варианта нужно внести в отчёт по достоверным сведениям. Они не
  восстанавливаются предположительно по автору Git-коммитов или имени архива.

Эти сведения относятся к оформлению и подтверждению учебной работы; все
перечисленные выше программные проверки описаны по фактическому результату.
