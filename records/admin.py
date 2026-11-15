from django.contrib import admin

from .models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "artist", "genre", "year")
    list_filter = ("genre", "year")
    search_fields = ("title", "artist")
    ordering = ("title", "id")
