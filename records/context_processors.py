"""Общие данные для всех страниц Vinyl Collection Service."""

from .models import Record


def vinyl_context(request):
    """Количество пластинок и имя сайта для общей навигации."""
    return {
        "site_name": "Vinyl Collection Service",
        "records_count": Record.objects.count(),
    }
