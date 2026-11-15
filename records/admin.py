"""Редактирование пластинок, архивных данных и связанных коллекций."""

from django.contrib import admin
from django.db.models import Count, Q

from collections_app.models import CollectionRecord

from .models import Record


class RecordCollectionInline(admin.TabularInline):
    model = CollectionRecord
    fields = ("collection", "status")
    autocomplete_fields = ("collection",)
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "artist", "genre", "year", "is_vintage",
        "collections_count",
    )
    list_display_links = ("title",)
    list_editable = ("genre",)
    list_filter = ("genre", "year", "is_vintage")
    search_fields = ("title", "artist")
    ordering = ("title", "id")
    list_per_page = 20
    readonly_fields = ("id", "slug", "is_vintage")
    inlines = (RecordCollectionInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _current_collections=Count(
                "collection_links", distinct=True,
                filter=Q(collection_links__status__in=(
                    CollectionRecord.Status.IN_COLLECTION,
                    CollectionRecord.Status.RESERVED,
                )),
            ),
        )

    @admin.display(
        description="Действующих коллекций", ordering="_current_collections",
    )
    def collections_count(self, obj):
        return obj._current_collections
