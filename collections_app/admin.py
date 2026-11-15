"""Администрирование коллекций и экземпляров винила."""

from django.contrib import admin
from django.db.models import Count, Q

from .models import Collection, CollectionRecord


class CollectionRecordInline(admin.TabularInline):
    model = CollectionRecord
    fields = ("record", "status")
    autocomplete_fields = ("record",)
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "current_records_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("name", "pk")
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (CollectionRecordInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _current_records=Count(
                "record_links", distinct=True,
                filter=Q(record_links__status__in=(
                    CollectionRecord.Status.IN_COLLECTION,
                    CollectionRecord.Status.RESERVED,
                )),
            ),
        )

    @admin.display(
        description="Пластинок в коллекции", ordering="_current_records",
    )
    def current_records_count(self, obj):
        return obj._current_records


@admin.register(CollectionRecord)
class CollectionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "collection", "record", "status", "release_year")
    list_display_links = ("id",)
    list_editable = ("status",)
    list_filter = ("status", "collection", "record__genre")
    list_select_related = ("collection", "record")
    search_fields = ("collection__name", "record__title", "record__artist")
    autocomplete_fields = ("collection", "record")
    ordering = ("collection__name", "record__title", "id")
    list_per_page = 20
    readonly_fields = ("id",)
    actions = ("mark_available", "mark_reserved", "mark_removed")

    @admin.display(description="Год", ordering="record__year")
    def release_year(self, obj):
        return obj.record.year or "—"

    @admin.action(description="Пометить выбранные как доступные")
    def mark_available(self, request, queryset):
        count = queryset.update(status=CollectionRecord.Status.IN_COLLECTION)
        self.message_user(request, f"Доступны для обмена: {count}.")

    @admin.action(description="Зарезервировать выбранные")
    def mark_reserved(self, request, queryset):
        count = queryset.current().update(
            status=CollectionRecord.Status.RESERVED,
        )
        self.message_user(request, f"Зарезервированы: {count}.")

    @admin.action(description="Вывести выбранные из коллекций")
    def mark_removed(self, request, queryset):
        count = queryset.update(status=CollectionRecord.Status.REMOVED)
        self.message_user(request, f"Выведены из коллекций: {count}.")
