# ПР9: соответствие требованиям индивидуального проекта

Документ сопоставляет результат доработки Vinyl Collection Service с 31 пунктом
чек-листа §7.2 и всеми 30 показателями оценивания §7.3 практической работы №9
«Модели Django, связи и операции с базой данных через ORM». Требования примера
Roomly адаптированы к пластинкам, коллекциям, пользователям и составу коллекций.
Наличие кода и успешных автоматических проверок рассматривается отдельно от
живой демонстрации в браузере и устного объяснения на защите.

## Подтверждённые результаты проверки

Проверки выполнены 15 ноября 2026 года:

| Проверка | Фактический результат |
| --- | --- |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check` | `No changes detected` |
| `python manage.py showmigrations` | Все существующие миграции отмечены `[X]`, включая `records.0001_initial`, `users.0001_initial`, `collections_app.0001_initial` |
| `pytest -v` | **81 passed, 44 subtests passed**, без предупреждений; результаты — `VERIFICATION.txt` |
| `flake8 . --extend-exclude=venv` | Замечаний нет; завершение с кодом `0` |
| Перенос ПР7 | **10 пластинок, 5 коллекций, 2 пользователя, 13 связей**; сохранены исходные идентификаторы, значения полей и пары связей |

Представления, маршруты, контекст и сформированный HTML проверены через
**Django Test Client**. Полноценная ручная проверка в браузере не выполнена:
ограничения среды запрещают Chromium необходимые операции с сокетами, а
доступный облачный браузер работает в другом окружении и не видит локальный
сервер проекта. Визуальная браузерная проверка и браузерные скриншоты в состав
подтверждений не включены.

Django Debug Toolbar установлен и подключён для локальной разработки.
Отдельные интеграционные тесты проверяют серверную загрузку SQL-панели
по AJAX, наличие JOIN и псевдонимов связанных полей, JavaScript-ресурс панели
и ограничения её показа. Открытие панели и взаимодействие с ней в настоящем
браузере пока не подтверждены.

## Где находятся проверки

В таблице используются сокращения с однозначным соответствием файлу и классу:

| Обозначение | Файл и класс |
| --- | --- |
| `M` | `tests/test_orm_models.py::ModelTests` |
| `V` | `tests/test_orm_views.py::ORMViewTests` |
| `I` | `tests/test_import_pr7.py::ImportTests` |
| `D` | `tests/test_demo_orm.py::DemoOrmTests` |
| `T` | `tests/test_debug_toolbar.py::DebugToolbarTests` |

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
| 22 | Получается сокращённый набор полей | `values_list("genre", flat=True).distinct()` для вариантов жанра; `values("genre_name")` для группировки; связанная проекция `link_rows` через `annotate(F(...)).values(...)` | `records/forms.py::RecordFilterForm.__init__`; `collections_app/views.py::statistics`; `V.test_statistics_projects_related_values_and_executes_join_query` |
| 23 | Реализовано агрегирование | `aggregate()` с `Count`, `Min`, `Max`, `Avg` в `collections_app/views.py::statistics` | `V.test_statistics_aggregate_real_records_and_ignore_unknown_years`; `V.test_empty_database_has_normal_pages_and_zero_statistics` |
| 24 | Реализованы аннотации и группировка | `Count("records", distinct=True)` у списка коллекций; аннотации по коллекциям и жанрам; `F("collection__name")` и `F("record__title")` в составе коллекций | `V.test_related_artist_filter_preserves_full_sizes_and_unique_rows`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years`; `V.test_statistics_projects_related_values_and_executes_join_query` |
| 25 | Реализован постраничный вывод | `Paginator(..., PAGE_SIZE)` в каталоге, списке коллекций и таблице состава коллекций; `get_page()` обрабатывает номер страницы | `V.test_catalog_is_ordered_and_has_five_items_per_page`; `V.test_invalid_page_numbers_use_safe_first_or_last_page`; `V.test_statistics_pagination_makes_every_link_accessible_once` |
| 26 | Навигация сохраняет поиск, фильтры и сортировку | `templates/includes/pagination.html`: `{% querystring page=... %}`; формы не передают старый параметр `page` | `V.test_search_filters_and_sort_survive_page_transition`; `V.test_collection_pagination_preserves_search` |
| 27 | ORM интегрирован в представления и шаблоны | `records/views.py`, `collections_app/views.py`; контекст поступает в существующие шаблоны соответствующих приложений | `V.test_previous_pages_are_available`; `V.test_details_and_related_objects_need_two_queries`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years` |
| 28 | Обработаны отсутствие объектов, пустые результаты и неправильный ввод | Формы в `records/forms.py`, `collections_app/forms.py`; `get_object_or_404()`; пустые состояния шаблонов; разрешённый словарь сортировки | `V.test_missing_objects_return_404`; `V.test_invalid_filter_parameters_show_errors_without_server_error`; `V.test_empty_database_has_normal_pages_and_zero_statistics`; `V.test_empty_search_and_sql_metacharacters_are_literal` |
| 29 | Проверены модели, связи, миграции, запросы и сценарии | Тесты `M`, `V`, `I`, `D`, `T`; сохранены прежние ООП-тесты; выполнены команды проверки | `81 passed, 44 subtests passed`; `check`: `0` замечаний; все миграции `[X]`; `makemigrations --check`: изменений нет; `flake8`: замечаний нет; подробности в `VERIFICATION.txt` |
| 30 | Актуализирован README; изменения фиксируются коммитами `PR9:` | `README.md`: модели, запуск, импорт и проверки; исходное состояние сохранено коммитом `f740e0b` с меткой `PR9:`; финальные коммиты проверяются в комплектном репозитории | `git log --oneline --grep="^PR9:"`; содержимое `README.md` и файлов `docs/` |
| 31 | Не менее 15 разных ORM-выражений с минимумами по категориям | [Реестр ORM-запросов](ORM_QUERIES.md) содержит 16 завершённых выборок, используемых страницами и формами | Подсчёт не включает импортер, `demo_orm`, тестовые запросы, промежуточные вызовы цепочки каталога и отдельный подсчёт `Paginator`; соответствие категориям приведено в реестре |

## Таблица оценивания §7.3: все 30 показателей

Таблица ниже отдельно проверяет конкретные показатели оценивания, включая
связанные `values()`, `F()` и Django Debug Toolbar. Она указывает реализацию
и автоматические подтверждения, а в последнем столбце — действие, которое
студент должен выполнить и объяснить на защите. **Живая демонстрация этих
действий в браузере и устная защита ещё не проведены.**

| № | Показатель §7.3 | Реализация и автоматическое подтверждение | Что показать и объяснить на защите |
| --- | --- | --- | --- |
| 1 | Описание модели, изменение типа/параметров поля | `records/models.py`, `users/models.py`, `collections_app/models.py`; `M.test_required_fields_and_email_are_validated`, `M.test_unknown_year_and_genre_are_supported` | Показать `blank`, `null`, `default`, типы полей; изменить допустимый параметр и объяснить влияние на проверку/хранение |
| 2 | Создание связи, параметры и последствия изменения | Два `ForeignKey` в `CollectionRecord`; `M.test_collection_deletion_removes_only_links`, `M.test_record_deletion_preserves_collection` | Показать `collection`, `record`, `on_delete=CASCADE`; объяснить, почему удаляется строка состава, а другая основная сущность сохраняется |
| 3 | Прямые и обратные связи | `collection.records`, `record.collections`, `record_links`, `collection_links`; `M.test_forward_and_reverse_relations` | Выполнить прямое и обратное обращение в shell; объяснить роль `related_name` |
| 4 | Создание и применение миграции после изменения модели | Три `0001_initial.py`, успешные `migrate`, `showmigrations`, `makemigrations --check`; результаты в `VERIFICATION.txt` | Показать модель и миграцию, выполнить `makemigrations` и `migrate`; объяснить изменение схемы |
| 5 | Создание объекта ORM | `collections_app/management/commands/demo_orm.py`; тесты CRUD в `M` и `D.test_crud_demonstration_keeps_existing_data_unchanged` | Создать учебный объект с выбранными значениями, повторно получить его и объяснить результат |
| 6 | Изменение объекта и `save()` | `demo_orm`; `M.test_crud_and_get_missing_multiple_objects`, `M.test_user_create_save_read_and_delete`, `M.test_collection_crud_and_membership_changes` | Изменить поле, вызвать `save()`, перечитать объект; различить изменение в памяти и запись в БД |
| 7 | Удаление и ограничения связей | `demo_orm`, `delete()` и проверки каскада в `M` | Удалить специально созданный объект, проверить отсутствие; объяснить влияние `CASCADE` на строки состава |
| 8 | `QuerySet`, получение набора и дополнительный фильтр | `records/views.py::_catalog_context`: `all()` и проверенные фильтры; `V.test_single_filter_and_year_range` | Получить все пластинки, добавить условие и показать изменение выборки |
| 9 | Фильтрация по полю связанной модели | `collections_app/views.py::collections`: `records__artist__iregex`; `V.test_related_artist_filter_preserves_full_sizes_and_unique_rows` | Изменить исполнителя; объяснить отличие пути к строковому полю связанной модели от фильтра по её ID |
| 10 | Несколько условий фильтрации | Диапазон годов, жанр, коллекция, поиск и известность года; `V.test_search_filters_and_sort_survive_page_transition` | В браузере применить несколько фильтров, изменить один и объяснить условие «И» |
| 11 | Преобразование и проверка пользовательского ввода | `RecordFilterForm`, `CollectionSearchForm`; `V.test_invalid_filter_parameters_show_errors_without_server_error` | Сравнить корректный год и `year_from=abc`, неправильный ID и сортировку; показать ошибки формы |
| 12 | Поле и направление сортировки | `RECORD_SORTS`, `order_by()`; `V.test_sort_by_several_fields`, `V.test_reverse_year_sort_and_one_sided_ranges` | Переключить `year`/`-year` и `artist`; объяснить устойчивый порядок при совпадениях |
| 13 | Сортировка из GET и разрешённый словарь | `records/forms.py::RECORD_SORTS`, поле `sort`; `V.test_invalid_filter_parameters_show_errors_without_server_error` | Показать значение по умолчанию, разрешённые ключи и обработку неизвестного; объяснить запрет произвольного `order_by` |
| 14 | `values()` с полями связанных сущностей | `collections_app/views.py::statistics`, запрос `link_rows`: семь ключей, включая имя коллекции и название пластинки; `V.test_statistics_projects_related_values_and_executes_join_query` | Выполнить проекцию в shell, показать словари, добавить/удалить поле и объяснить структуру результата |
| 15 | `annotate()` и `F()` с применением результата | `collection_name=F("collection__name")`, `record_title=F("record__title")`, `record_artist`, `record_year`; значения используются в `values()` и `statistics.html`; `V.test_statistics_projects_related_values_and_executes_join_query` | Показать псевдонимы связанных полей, их вывод в таблице; изменить выражение или добавить псевдоним |
| 16 | Получение объекта и обработка отсутствия | `get_object_or_404()` в обеих карточках; `V.test_missing_objects_return_404` | Открыть существующий ID и несуществующий ID; объяснить ответ 404 |
| 17 | Подсчёт и изменение условия агрегации | `count()`, `aggregate()`, `Count`, `Q` в `statistics`; `V.test_statistics_aggregate_real_records_and_ignore_unknown_years` | Сопоставить итоги с БД, изменить условие учёта неизвестных годов и объяснить результат |
| 18 | Статистика по связанным объектам | `Collection.objects.annotate(records_count=Count("records"))` с сортировкой по размеру; `V.test_empty_collections_remain_in_lists_statistics_and_details` | Показать число пластинок для коллекций, изменить сортировку и объяснить сохранение пустых коллекций |
| 19 | `select_related()` и SQL в Django Debug Toolbar | `collection_detail`: `select_related("record")`; `demo_orm` показывает оба FK; `V.test_details_and_related_objects_need_two_queries`, `M.test_select_related_loads_both_foreign_keys_in_one_query`; панель подключена в settings/urls и проверена тестами `T` | В локальном браузере открыть карточку коллекции → Toolbar → SQL, показать JOIN; изменить набор `select_related` и объяснить число запросов |
| 20 | Необходимые связанные поля через `values()`/`annotate()` и SQL-панель | Рабочая таблица `link_rows` на странице статистики; `V.test_statistics_projects_related_values_and_executes_join_query`; `T.test_local_page_has_sql_panel_with_join_and_projected_fields` проверяет AJAX-ответ SQL-панели с JOIN и псевдонимами | В локальном браузере показать SQL проекции; объяснить набор выбранных столбцов и отсутствие необходимости в дополнительном `select_related()` для словарей |
| 21 | Передача контекста и имя переменной в шаблоне | `statistics` передаёт `link_rows`; `collections_app/templates/collections/statistics.html` выводит его; `V.test_statistics_projects_related_values_and_executes_join_query` | Согласованно переименовать переменную в view и шаблоне; объяснить последствия изменения только одной стороны |
| 22 | Размер страницы и `Paginator` | `PAGE_SIZE` в обоих файлах views; подписи каталога и таблицы состава используют `page_obj.paginator.per_page`; `V.test_catalog_is_ordered_and_has_five_items_per_page`, `V.test_statistics_pagination_makes_every_link_accessible_once` | Изменить размер, сравнить количество страниц и записей. Серверная проверка смены размера на 3 описана в `VERIFICATION.txt` |
| 23 | Навигация и номер страницы | `templates/includes/pagination.html`: `page_obj`, `has_previous`, `has_next`; `V.test_invalid_page_numbers_use_safe_first_or_last_page`, `V.test_statistics_pagination_makes_every_link_accessible_once` | Перейти вперёд и назад, показать первую/последнюю страницу и обработку неправильного номера |
| 24 | Сохранение GET-параметров в ссылках пагинации | `{% querystring page=... %}`; `V.test_search_filters_and_sort_survive_page_transition`, `V.test_collection_pagination_preserves_search` | После выбора фильтров/сортировки перейти на следующую страницу и показать сохранившиеся параметры URL |
| 25 | Совместная работа фильтров, сортировки и пагинации | `_catalog_context` применяет операции в указанном порядке; `V.test_search_filters_and_sort_survive_page_transition` | В браузере изменить один параметр и объяснить состав/порядок результата и сброс номера страницы при отправке формы |
| 26 | Сохранение объектов без связанных строк | Аннотация от `Collection` сохраняет пустые коллекции; `V.test_empty_collections_remain_in_lists_statistics_and_details` | Показать коллекцию с нулём пластинок, объяснить выбор исходной модели и результат соединения |
| 27 | Исключение через `exclude()` | Исключение `year=0` и `NULL` в каталоге/статистике; `V.test_exclude_unknown_years` | Изменить условие исключения в shell, показать удалённые из результата записи |
| 28 | Ограничение выборки срезом или пагинацией | `uncollected[:5]`; `V.test_statistics_limits_uncollected_preview_to_five_records`; рабочие `Paginator` | Изменить границы среза и объяснить число полученных объектов либо показать иной размер страницы |
| 29 | `get()`, отсутствие записи и несколько совпадений | `demo_orm`, `M.test_crud_and_get_missing_multiple_objects` | В shell показать обычный `get()`, `DoesNotExist`, `MultipleObjectsReturned`; сравнить с `get_object_or_404()` |
| 30 | Связанные модели, ORM-запрос и результат в представлении | `records/views.py`, `collections_app/views.py`, связанные шаблоны; проверки маршрутов, контекста, связанных строк и статистики в `V` | Изменить условие запроса, проверить страницу в браузере и объяснить изменение при сохранении прежних сценариев |

Для пунктов 14, 15 и 20 используется **реальная таблица состава коллекций**,
а не отдельный учебный запрос без вывода в приложении. Для пунктов 19 и 20
настроена Django Debug Toolbar 6.2.0; интеграционный тест получает SQL-панель
её AJAX-маршрутом и проверяет SQL. Запросы с внешнего IP и с `DEBUG=False`
проверяют `T.test_nonlocal_request_does_not_receive_toolbar` и
`T.test_debug_false_does_not_receive_toolbar`.

Программные точки для всех перечисленных показателей представлены в проекте.
Там, где методичка требует действия в браузере, изменения кода на месте и
устного объяснения, студент должен выполнить их при локальной проверке и
защите. Таблица не удостоверяет уже состоявшуюся защиту или визуальный просмотр.

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

Открывайте проект по `http://127.0.0.1:8000/` при `DEBUG=True` и установленных
зависимостях. Для SQL-демонстрации раскройте Django Debug Toolbar и выберите
SQL. Панель доступна локально; в обычном запуске тестов и при `DEBUG=False`
она отключена. Заранее подготовьте вкладки с каталогом, карточкой коллекции,
статистикой и кодом запросов.

| Время | Что показать | Что объяснить |
| --- | --- | --- |
| 0:00–0:40 | Три файла моделей и `collections_app/migrations/0001_initial.py` | Четыре модели; M2M через два `ForeignKey`; уникальная пара, `CASCADE`, обратные имена |
| 0:40–1:10 | `python manage.py check`, `python manage.py showmigrations` | Настройки без ошибок; миграции применены к `db.sqlite3`; исходная база сохранена |
| 1:10–1:50 | `/records/?year_from=1950&year_to=2000&known_year=1&sort=-year`; переход на вторую страницу | Фильтрация → сортировка → пагинация; параметры сохраняются. `year_from=abc` показывает ошибку формы |
| 1:50–2:25 | `/collections/?artist=Pink`; карточка `/collections/1/` → Toolbar → SQL | Фильтр по связанному исполнителю; JOIN при `select_related("record")`; отличие от обращения к FK без предварительной загрузки |
| 2:25–3:30 | `/collections/statistics/`: таблица «Состав коллекций», запрос `link_rows`, Toolbar → SQL | `annotate(F(...)).values(...)` выбирает связанные поля, возвращает словари и делает JOIN; показать псевдонимы `collection_name`/`record_title`; итоги `10 / 5 / 2 / 13` |
| 3:30–4:05 | `python manage.py demo_orm` | Реальные `create/get/save/delete`, изменение FK, обязательный откат временной транзакции |
| 4:05–5:00 | Следующий пример Django shell, `/admin/`, итог проверок и Git | Прямые/обратные связи; зарегистрированные модели; `VERIFICATION.txt` и `git log --oneline --grep="^PR9:"` |

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
