"""Коллекции и сводная статистика на основе Django ORM."""

import re

from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q, Value
from django.db.models.functions import Coalesce, NullIf
from django.shortcuts import get_object_or_404, render

from records.models import Record
from users.models import User

from .forms import CollectionSearchForm
from .models import Collection, CollectionRecord


PAGE_SIZE = 5


def collections(request):
    form = CollectionSearchForm(request.GET)
    queryset = Collection.objects.annotate(
        records_count=Count("records", distinct=True),
    )
    if form.is_valid():
        if form.cleaned_data["q"]:
            # SQLite LIKE не учитывает регистр кириллицы.
            # Экранированный iregex ищет буквальный текст и Unicode-регистр.
            queryset = queryset.filter(
                name__iregex=re.escape(form.cleaned_data["q"]),
            )
        if form.cleaned_data["artist"]:
            # Count до фильтра сохраняет полный размер найденной коллекции.
            queryset = queryset.filter(
                records__artist__iregex=re.escape(form.cleaned_data["artist"]),
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
    # ForeignKey позволяет получить пластинку без отдельного запроса на строку.
    links = collection.record_links.select_related("record").order_by(
        "record__title", "record__pk",
    )
    return render(
        request, "collections/collection_detail.html",
        {"collection": collection, "records": [link.record for link in links]},
    )


def statistics(request):
    stats = Record.objects.aggregate(
        total_records=Count("pk"),
        total_artists=Count("artist", distinct=True),
    )
    stats["total_collections"] = Collection.objects.count()
    stats["total_users"] = User.objects.count()
    stats["total_links"] = CollectionRecord.objects.count()
    year_stats = Record.objects.exclude(
        Q(year=0) | Q(year__isnull=True),
    ).aggregate(
        oldest_year=Min("year"), newest_year=Max("year"),
        average_year=Avg("year"), known_year_records=Count("pk"),
    )
    by_collection = Collection.objects.annotate(
        records_count=Count("records"),
    ).order_by("-records_count", "name", "pk")
    by_genre = Record.objects.annotate(
        genre_name=Coalesce(NullIf("genre", Value("")), Value("Не указан")),
    ).values("genre_name").annotate(
        records_count=Count("pk"),
    ).order_by("-records_count", "genre_name")
    uncollected = Record.objects.filter(collections__isnull=True).order_by(
        "title", "pk",
    )
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
        {"stats": stats, "year_stats": year_stats,
         "by_collection": by_collection, "by_genre": by_genre,
         "uncollected_count": uncollected.count(),
         "uncollected": uncollected[:5],
         "link_rows": page_obj.object_list, "page_obj": page_obj},
    )
