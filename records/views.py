"""Каталог и поиск: все рабочие выборки выполняются Django ORM."""

from datetime import date
from re import escape

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .forms import RECORD_SORTS, RecordFilterForm
from .models import Record


PAGE_SIZE = 5


def _catalog_context(request, *, require_query=False):
    form = RecordFilterForm(request.GET)
    queryset = Record.objects.all()
    if form.is_valid():
        filters = form.cleaned_data
        query = filters.get("q", "")
        if require_query and not query:
            queryset = queryset.none()
        if query:
            scope = filters.get("scope") or "all"
            # SQLite icontains учитывает регистр кириллицы; iregex использует
            # Unicode. escape() сохраняет буквальный смысл пользовательского q.
            lookup = "icontains" if query.isascii() else "iregex"
            value = query if query.isascii() else escape(query)
            title_match = Q(**{f"title__{lookup}": value})
            artist_match = Q(**{f"artist__{lookup}": value})
            if scope == "title":
                queryset = queryset.filter(title_match)
            elif scope == "artist":
                queryset = queryset.filter(artist_match)
            else:
                queryset = queryset.filter(title_match | artist_match)
        if filters.get("genre"):
            queryset = queryset.filter(genre=filters["genre"])
        start, end = filters.get("year_from"), filters.get("year_to")
        if start is not None or end is not None:
            queryset = queryset.filter(
                year__gte=start if start is not None else 1900,
                year__lte=end if end is not None else date.today().year,
            )
        if filters.get("collection"):
            queryset = queryset.filter(
                collections__pk=filters["collection"].pk,
            )
        if filters.get("known_year"):
            queryset = queryset.exclude(Q(year=0) | Q(year__isnull=True))
        sort = filters.get("sort") or "title"
    else:
        # Не выполняем частичный запрос с ошибочными параметрами.
        queryset = Record.objects.none()
        sort = "title"
    queryset = queryset.order_by(*RECORD_SORTS[sort])
    page_obj = Paginator(queryset, PAGE_SIZE).get_page(request.GET.get("page"))
    return {
        "form": form,
        "page_obj": page_obj,
        "records": page_obj.object_list,
        "results": page_obj.object_list,
        "query": (request.GET.get("q") or "").strip(),
    }


def records(request):
    return render(
        request, "records/record_list.html", _catalog_context(request),
    )


def record_detail(request, record_id):
    record = get_object_or_404(
        Record.objects.prefetch_related("collections"), pk=record_id,
    )
    return render(
        request, "records/record_detail.html",
        {"record": record, "collections": record.collections.all()},
    )


def search_records(request):
    return render(
        request, "records/search.html",
        _catalog_context(request, require_query=True),
    )
