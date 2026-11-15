# ПР9: реестр ORM-выражений

Реестр подготовлен по §2.5 и пункту 31 §7.2 практической работы №9. В итоговом
подсчёте учтены **16 различных завершённых выборок**, которые используются
реальными страницами и формами Vinyl Collection Service.

## Правила подсчёта

- Вся динамическая цепочка каталога — от `Record.objects.all()` до проверки
  фильтров, сортировки и выборки страницы — учитывается **один раз**.
  Промежуточные `filter()`, `exclude()` и `order_by()` внутри этой цепочки
  отдельно к общему количеству не прибавляются.
- Список коллекций с поиском и фильтром исполнителя также учитывается один раз.
- Связанная проекция состава коллекций `annotate(F(...)).values(...)` вместе
  с сортировкой и пагинацией учитывается как одно выражение №16. Служебный
  подсчёт строк внутри `Paginator` не добавляется к общему количеству.
- Карточка пластинки вместе с `prefetch_related()` считается одним выражением,
  хотя загрузка основной записи и связанных коллекций использует два SQL-запроса.
- Итоговое количество не включает запросы импортера, демонстрации `demo_orm`,
  автоматических тестов и админки. Они подтверждают дополнительные возможности
  ORM и правильность поведения.
- Количество пластинок вне коллекций и ограниченный список этих пластинок —
  самостоятельные завершённые выборки: первая вычисляет общее число, вторая
  получает не более пяти объектов для отображения.
- Повторная аннотированная выборка коллекций на странице статистики и
  `record.collections.all()` после `prefetch_related()` не увеличивают итог.
  Реестр поэтому не зависит от подсчёта близких вариантов одного запроса.

В таблице стрелка обозначает продолжение одной динамической цепочки в коде.
Многоточие в сводном описании агрегата раскрывается в пояснениях ниже.

## 16 завершённых выборок

| № | Выражение и назначение | Где используется |
| --- | --- | --- |
| 1 | `Record.objects.all()` → проверенные поиск/фильтры → `order_by(*RECORD_SORTS[sort])` → `Paginator(...).get_page(...)`. Получение страницы каталога или результатов поиска | `records/views.py::_catalog_context`; `/records/`, `/records/search/` |
| 2 | `Record.objects.exclude(genre__isnull=True).exclude(genre="").order_by("genre").values_list("genre", flat=True).distinct()`. Уникальные известные жанры | `records/forms.py::RecordFilterForm.__init__`; варианты поля «Жанр» |
| 3 | `Collection.objects.order_by("name", "pk")`. Полный упорядоченный набор вариантов коллекции | `records/forms.py::RecordFilterForm.__init__`; `ModelChoiceField` «Коллекция» |
| 4 | `get_object_or_404(Record.objects.prefetch_related("collections"), pk=record_id)`. Пластинка и её коллекции | `records/views.py::record_detail`; `/records/<id>/` |
| 5 | `Collection.objects.annotate(records_count=Count("records", distinct=True))` → проверенные фильтры имени/исполнителя → `order_by("name", "pk")` → `Paginator(...).get_page(...)`. Страница коллекций с их полным размером | `collections_app/views.py::collections`; `/collections/` |
| 6 | `get_object_or_404(Collection, pk=collection_id)`. Одна коллекция по идентификатору | `collections_app/views.py::collection_detail`; `/collections/<id>/` |
| 7 | `collection.record_links.select_related("record").order_by("record__title", "record__pk")`. Состав коллекции со сведениями о каждой пластинке | `collections_app/views.py::collection_detail`; список в карточке коллекции |
| 8 | `Record.objects.aggregate(total_records=Count("pk"), total_artists=Count("artist", distinct=True))`. Количество пластинок и разных исполнителей | `collections_app/views.py::statistics`; сводка каталога |
| 9 | `Collection.objects.count()`. Общее количество коллекций | `collections_app/views.py::statistics`; `stats["total_collections"]` |
| 10 | `User.objects.count()`. Количество пользователей предметной области | `collections_app/views.py::statistics`; `stats["total_users"]` |
| 11 | `CollectionRecord.objects.count()`. Количество включений пластинок в коллекции | `collections_app/views.py::statistics`; `stats["total_links"]` |
| 12 | `Record.objects.exclude(Q(year=0) \| Q(year__isnull=True)).aggregate(...)`. Минимальный, максимальный, средний год и количество записей с известным годом | `collections_app/views.py::statistics`; `year_stats` |
| 13 | `Record.objects.annotate(genre_name=Coalesce(NullIf("genre", Value("")), Value("Не указан"))).values("genre_name").annotate(records_count=Count("pk")).order_by("-records_count", "genre_name")`. Количество пластинок по жанрам | `collections_app/views.py::statistics`; `by_genre` |
| 14 | `uncollected.count()`, где `uncollected = Record.objects.filter(collections__isnull=True).order_by("title", "pk")`. Полное число пластинок вне коллекций | `collections_app/views.py::statistics`; заголовок раздела «Вне коллекций» |
| 15 | `uncollected[:5]` для того же базового набора. Первые пять пластинок вне коллекций по названию | `collections_app/views.py::statistics`; ограниченный список со ссылками на карточки |
| 16 | `CollectionRecord.objects.annotate(collection_name=F("collection__name"), record_title=F("record__title"), record_artist=F("record__artist"), record_year=F("record__year")).values("id", "collection_id", "record_id", "collection_name", "record_title", "record_artist", "record_year").order_by("collection_name", "record_title", "id")` → `Paginator(...).get_page(...)`. Страница словарей с необходимыми полями двух связанных моделей | `collections_app/views.py::statistics`; `link_rows` и таблица «Состав коллекций» на `/collections/statistics/` |

Агрегат №12 в точности содержит:

```python
Record.objects.exclude(
    Q(year=0) | Q(year__isnull=True),
).aggregate(
    oldest_year=Min("year"),
    newest_year=Max("year"),
    average_year=Avg("year"),
    known_year_records=Count("pk"),
)
```

Для №9–11 подсчитываются разные сущности и выводятся самостоятельные показатели.
Пластинка, входящая в три коллекции, увеличивает №8 на одну запись, а №11 —
на три включения. Эти показатели имеют разный смысл.

## Минимумы по категориям из §2.5

Одна выборка может подтверждать несколько тематических категорий. Это не
увеличивает число 16 в реестре. Разные пользовательские сценарии фильтрации
ниже подтверждают требуемые виды фильтров, но их промежуточные вызовы не
учитываются как дополнительные завершённые выражения общего списка.

| Категория | Минимум | Реальные примеры из проекта | Основные проверки |
| --- | ---: | --- | --- |
| Базовое получение | 2 | Набор пластинок №1; отдельная пластинка №4 и отдельная коллекция №6 через `get_object_or_404()` | `test_catalog_is_ordered_and_has_five_items_per_page`; `test_details_and_related_objects_need_two_queries`; `test_missing_objects_return_404` |
| Фильтрация | 4 | Одно условие: `filter(genre=...)`; несколько условий: `filter(year__gte=..., year__lte=...)`; связанное строковое поле: `filter(records__artist__iregex=re.escape(...))` в списке коллекций; исключение: `exclude(Q(year=0) \| Q(year__isnull=True))` | `test_single_filter_and_year_range`; `test_related_artist_filter_preserves_full_sizes_and_unique_rows`; `test_exclude_unknown_years`; `test_search_filters_and_sort_survive_page_transition` |
| Поиск | 2 | По одному полю `title` при `scope=title`; по `title OR artist` при `scope=all`. Дополнительно — поиск коллекции по `name` | `test_search_uses_title_or_artist_and_scopes`; `test_collection_search_handles_cyrillic_case_and_literal_symbols`; `test_record_search_handles_cyrillic_case_and_literal_symbols` |
| Сортировка | 2 | По одному полю: `order_by("genre")` в №2; по нескольким полям: исполнитель → год → название → PK в каталоге; по связанному полю: `record__title` в №7 | `test_sort_by_several_fields`; `test_reverse_year_sort_and_one_sided_ranges`; `test_catalog_is_ordered_and_has_five_items_per_page`; просмотр `records/forms.py` |
| Работа со связями | 2 | `prefetch_related("collections")` в №4; `collection.record_links.select_related("record")` в №7; доступ к прямым и обратным связям | `test_details_and_related_objects_need_two_queries`; `test_forward_and_reverse_relations`; `test_select_related_loads_both_foreign_keys_in_one_query` |
| Агрегирование и аннотирование | 2 | Сводные `aggregate()` в №8 и №12; аннотация размера коллекций №5; группировка жанров через `values().annotate()` в №13; связанные псевдонимы `annotate(...=F(...))` в №16 | `test_statistics_aggregate_real_records_and_ignore_unknown_years`; `test_empty_collections_remain_in_lists_statistics_and_details`; `test_statistics_projects_related_values_and_executes_join_query` |
| Постраничный вывод | 1 | `Paginator(queryset, PAGE_SIZE).get_page(...)` в №1, №5 и №16; ссылки с `{% querystring page=... %}` | `test_search_filters_and_sort_survive_page_transition`; `test_collection_pagination_preserves_search`; `test_invalid_page_numbers_use_safe_first_or_last_page`; `test_statistics_pagination_makes_every_link_accessible_once` |

Указанные методы `test_...` находятся в `tests/test_orm_views.py::ORMViewTests`,
кроме `test_forward_and_reverse_relations` и
`test_select_related_loads_both_foreign_keys_in_one_query`, расположенных в
`tests/test_orm_models.py::ModelTests`.

## Связанные поля, F() и SQL-панель: пункты 14, 15, 19, 20 §7.3

Выборка №16 получает строки `CollectionRecord` и выбирает конкретные поля
двух связанных сущностей. Это самостоятельная рабочая проекция состава
коллекций; группировка жанров №13 решает другую задачу.

```python
link_rows = CollectionRecord.objects.annotate(
    collection_name=F("collection__name"),
    record_title=F("record__title"),
    record_artist=F("record__artist"),
    record_year=F("record__year"),
).values(
    "id", "collection_id", "record_id", "collection_name",
    "record_title", "record_artist", "record_year",
).order_by("collection_name", "record_title", "id")
```

`F()` обращается к полю в базе данных, а `annotate()` задаёт понятные имена
результата. После `values()` каждая строка — словарь с семью указанными
ключами. Представление передаёт страницу таких строк как `link_rows`;
`collections_app/templates/collections/statistics.html` использует
`link.collection_name`, `link.record_title`, `link.record_artist` и
`link.record_year` в таблице со ссылками на карточки.

`select_related()` здесь не нужен: при обращении к `collection__name` и
`record__title` ORM уже строит необходимые JOIN, а `values()` получает
конкретные столбцы вместо полных экземпляров связанных моделей. Для карточки
коллекции применяется другой подход: `collection.record_links.select_related(
"record")` возвращает объекты связи с заранее загруженными пластинками.

В проект установлен `django-debug-toolbar==6.2.0`. Настройки находятся в
`vinyl_project/settings.py`, маршруты — в `vinyl_project/urls.py`.
Приложение и middleware панели подключаются при `DEBUG=True` вне обычного
тестового запуска. Показ панели ограничен `INTERNAL_IPS` — `127.0.0.1` и `::1`.
После локального запуска можно открыть `/collections/statistics/`, раскрыть
Django Debug Toolbar → SQL и найти SELECT с `collection_name`, `record_title`
и соединениями таблиц коллекций и пластинок. На `/collections/1/` можно
показать запрос с `select_related("record")`.

Реализованы следующие автоматические подтверждения:

- `tests/test_orm_views.py::ORMViewTests::test_statistics_projects_related_values_and_executes_join_query`
  проверяет словарные ключи, значения из обеих связанных моделей, ссылки
  карточек и фактически выполненный SQL с двумя JOIN и псевдонимами.
- `test_statistics_pagination_makes_every_link_accessible_once` в том же
  классе проверяет доступность всех строк через страницы, порядок и отсутствие
  повторов.
- `tests/test_debug_toolbar.py::DebugToolbarTests::test_local_page_has_sql_panel_with_join_and_projected_fields`
  извлекает из HTML адрес AJAX-загрузки SQL-панели, запрашивает её и проверяет
  ответ с `INNER JOIN` и связанными псевдонимами, а также наличие
  JavaScript-ресурса панели.
- `test_nonlocal_request_does_not_receive_toolbar` и
  `test_debug_false_does_not_receive_toolbar` в том же классе проверяют
  ограничения показа панели.

Эти тесты подтверждают реализацию и серверную интеграцию. **Живая браузерная
демонстрация SQL-панели ещё не выполнена.** Действия с панелью и объяснение
изменённых запросов остаются частью локальной проверки и защиты студентом.

## Существенные детали реализации

### Проверка параметров и порядок операций

`RecordFilterForm` проверяет разрешённые жанры, существование коллекции,
числовые границы годов, длину строки и допустимые значения `scope`, `sort`,
`known_year`. Начало диапазона не может быть позже конца, а год — позже
текущего. При ошибке пользователь видит сообщения формы и пустой набор
результатов. Произвольный пользовательский текст не передаётся в `order_by()`:
поля выбираются из словаря `RECORD_SORTS`.

Последовательность в каталоге: проверка формы → поиск и фильтрация →
сортировка → пагинация. `pk` добавлен в сортировку как устойчивый критерий
для совпадающих названий/годов. Шаблон пагинации сохраняет GET-параметры;
отправка формы фильтров начинает новый просмотр с первой страницы.

### Поиск текста и кириллица

Для ASCII-запросов пластинок используются `icontains` и `Q`-условия. SQLite
не обеспечивает Unicode-регистронезависимость обычного `LIKE`, поэтому для
не-ASCII запросов пластинок применяется `iregex` с `re.escape()`. Поиск имени
коллекции и связанного исполнителя также использует экранированный `iregex`.
Пользовательская строка интерпретируется буквально: скобки, точки, `+` и
другие символы не превращаются в произвольное регулярное выражение.

### Связанные фильтры и корректные количества

`records__artist__iregex` фильтрует коллекции по имени исполнителя пластинки,
а не только по внешнему ключу. Аннотация размера коллекции создаётся до этого
фильтра; `Count("records", distinct=True)` и `distinct()` предотвращают
умножение счётчика и повторение строк при совпадении нескольких пластинок.
В результате пользователь видит полный размер каждой найденной коллекции.

Коллекции без пластинок сохраняются в списке и статистике с количеством `0`,
когда фильтр по исполнителю не задан. Для лет `0` и `NULL` принят смысл
«неизвестно»; такие значения не искажают `Min`, `Max` и `Avg`. Пустой каталог
даёт нулевые счётчики и понятное сообщение об отсутствии известных годов.

### CRUD и перенос данных

CRUD реализован админкой и безопасной командой `demo_orm`. Команда показывает
`create()`, `get()`, `save()`, `delete()` для всех четырёх моделей, затем
обязательно откатывает временную транзакцию. Импортер `import_pr7` сохраняет
ID и связи, использует ORM для записи и не перезаписывает конфликтующие
данные. Эти операции не включены в число 16.

## Результат проверки

Актуальный полный запуск: **81 passed, 44 subtests passed**, без предупреждений.
`python manage.py check` — `0` замечаний; все миграции `[X]`;
`makemigrations --check` — `No changes detected`; `flake8` — замечаний нет.
Полный вывод приведён в [VERIFICATION.txt](VERIFICATION.txt). В целевой базе
после переноса исходных данных: **10 пластинок, 5 коллекций, 2 пользователя
и 13 связей**. Дополнительно серверным клиентом проверены рабочая
конфигурация Toolbar, AJAX-ответ SQL-панели, отключение при `DEBUG=False`
и изменение размера страницы на 3 с согласованными подписями.

Сценарии запросов и HTML-ответы проверены через Django Test Client. Ручная
браузерная проверка не подтверждена из-за ограничений окружения. Привязка к
31 пункту §7.2 и ко всем 30 показателям §7.3 находится в
[чек-листе ПР9](PR9_CHECKLIST.md).
