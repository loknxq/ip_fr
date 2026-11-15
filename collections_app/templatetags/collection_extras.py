"""Человекочитаемое отображение TextChoices в словарных ORM-проекциях."""

from django import template

from collections_app.models import CollectionRecord

register = template.Library()


@register.filter
def placement_status_label(status):
    return dict(CollectionRecord.Status.choices).get(status, status)
