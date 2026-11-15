from django.contrib import admin

from .models import Collection, CollectionRecord


class CollectionRecordInline(admin.TabularInline):
    model = CollectionRecord
    extra = 1
    autocomplete_fields = ("record",)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = (CollectionRecordInline,)


@admin.register(CollectionRecord)
class CollectionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "collection", "record")
    list_select_related = ("collection", "record")
    search_fields = ("collection__name", "record__title", "record__artist")
    autocomplete_fields = ("collection", "record")
