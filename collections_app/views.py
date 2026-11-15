"""Коллекции и сводная статистика: операции выполняются через Django ORM."""

import re

from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q, Value
from django.db.models.functions import Coalesce, NullIf
from django.shortcuts import get_object_or_404, render

from records.models import Record
from users.models import User

from .forms import CollectionSearchForm, PlacementFilterForm, PLACEMENT_SORTS
from .models import Collection, CollectionRecord


PAGE_SIZE = 5
CURRENT_STATES = (
    CollectionRecord.Status.IN_COLLECTION,
    CollectionRecord.Status.RESERVED,
)


def collections(request):
    form = CollectionSearchForm(request.GET)
    queryset = Collection.objects.annotate(
        records_count=Count(
            "record_links", distinct=True,
            filter=Q(record_links__status__in=CURRENT_STATES),
        ),
    )
    if form.is_valid():
        if form.cleaned_data["q"]:
            # SQLite LIKE не учитывает регистр кириллицы.
            queryset = queryset.filter(
                name__iregex=re.escape(form.cleaned_data["q"]),
            )
        if form.cleaned_data["artist"]:
            # Учитываются только пластинки, находящиеся в коллекциях.
            queryset = queryset.filter(
                record_links__status__in=CURRENT_STATES,
                record_links__record__artist__iregex=re.escape(
                    form.cleaned_data["artist"],
                ),
            ).distinct()
    else:
        queryset = queryset.none()
    queryset = queryset.order_by("name", "pk")
    page_obj = Paginator(queryset, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(
        request, "collections/collection_list.html",
        {"collections": page_obj.object_list, "form": form,
         "page_obj": page_obj},
    )


def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    # JOIN для пластинок: нет запроса на каждую строку списка.
    placements = list(
        collection.record_links.current().select_related("record").order_by(
            "record__title", "record__pk",
        ),
    )
    return render(
        request, "collections/collection_detail.html",
        {"collection": collection,
         "placements": placements,
         "records": [placement.record for placement in placements]},
    )


def placements(request):
    """История связей с валидируемыми фильтрами и одним JOIN для таблицы."""
    form = PlacementFilterForm(request.GET)
    queryset = CollectionRecord.objects.all()
    if form.is_valid():
        filters = form.cleaned_data
        if filters["collection"]:
            queryset = queryset.for_collection(filters["collection"])
        if filters["status"]:
            queryset = queryset.filter(status=filters["status"])
        if filters["available_only"]:
            queryset = queryset.available()
        if filters["q"]:
            text = filters["q"]
            lookup = "icontains" if text.isascii() else "iregex"
            value = text if text.isascii() else re.escape(text)
            queryset = queryset.filter(
                Q(**{f"record__title__{lookup}": value})
                | Q(**{f"record__artist__{lookup}": value})
                | Q(**{f"collection__name__{lookup}": value}),
            )
        if filters["year_from"] is not None:
            queryset = queryset.filter(
                record__year__gte=filters["year_from"],
            )
        if filters["year_to"] is not None:
            queryset = queryset.filter(
                record__year__lte=filters["year_to"],
            )
        sort = filters["sort"] or "collection"
    else:
        queryset = queryset.none()
        sort = "collection"

    # F() подставляет значения связанных таблиц в SELECT через JOIN.
    # При values() select_related() не нужен: дополнительных запросов нет.
    queryset = queryset.annotate(
        collection_name=F("collection__name"),
        record_title=F("record__title"),
        record_artist=F("record__artist"),
        record_year=F("record__year"),
        record_vintage=F("record__is_vintage"),
    ).values(
        "id", "collection_id", "record_id", "status", "collection_name",
        "record_title", "record_artist", "record_year", "record_vintage",
    ).order_by(*PLACEMENT_SORTS[sort])
    page_obj = Paginator(queryset, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(
        request, "collections/placements.html",
        {"form": form, "page_obj": page_obj,
         "placements": page_obj.object_list},
    )


def placement_detail(request, placement_id):
    placement = get_object_or_404(
        CollectionRecord.objects.select_related("record", "collection"),
        pk=placement_id,
    )
    return render(
        request, "collections/placement_detail.html",
        {"placement": placement},
    )


def statistics(request):
    stats = Record.objects.aggregate(
        total_records=Count("pk"),
        total_artists=Count("artist", distinct=True),
    )
    stats["total_collections"] = Collection.objects.count()
    stats["total_users"] = User.objects.count()
    # Историческое число всех созданных связей — в т.ч. выведенных.
    stats["total_links"] = CollectionRecord.objects.count()
    status_counts = CollectionRecord.objects.aggregate(
        current=Count("pk", filter=Q(status__in=CURRENT_STATES)),
        available=Count(
            "pk", filter=Q(status=CollectionRecord.Status.IN_COLLECTION),
        ),
        reserved=Count(
            "pk", filter=Q(status=CollectionRecord.Status.RESERVED),
        ),
        removed=Count(
            "pk", filter=Q(status=CollectionRecord.Status.REMOVED),
        ),
    )
    year_stats = Record.objects.exclude(
        Q(year=0) | Q(year__isnull=True),
    ).aggregate(
        oldest_year=Min("year"), newest_year=Max("year"),
        average_year=Avg("year"), known_year_records=Count("pk"),
    )
    by_collection = Collection.objects.annotate(
        records_count=Count(
            "record_links", distinct=True,
            filter=Q(record_links__status__in=CURRENT_STATES),
        ),
    ).order_by("-records_count", "name", "pk")
    by_genre = Record.objects.annotate(
        genre_name=Coalesce(NullIf("genre", Value("")), Value("Не указан")),
    ).values("genre_name").annotate(
        records_count=Count("pk"),
    ).order_by("-records_count", "genre_name")
    uncollected = Record.objects.exclude(
        collection_links__status__in=CURRENT_STATES,
    ).order_by("title", "pk")
    link_rows = CollectionRecord.objects.annotate(
        collection_name=F("collection__name"),
        record_title=F("record__title"),
        record_artist=F("record__artist"),
        record_year=F("record__year"),
    ).values(
        "id", "collection_id", "record_id", "collection_name",
        "record_title", "record_artist", "record_year",
    ).order_by("collection_name", "record_title", "id")
    page_obj = Paginator(link_rows, PAGE_SIZE).get_page(
        request.GET.get("page"),
    )
    return render(
        request, "collections/statistics.html",
        {"stats": stats, "status_counts": status_counts,
         "year_stats": year_stats, "by_collection": by_collection,
         "by_genre": by_genre, "uncollected_count": uncollected.count(),
         "uncollected": uncollected[:5], "link_rows": page_obj.object_list,
         "page_obj": page_obj},
    )
