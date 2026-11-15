"""Коллекции винила, связи с пластинками и состояние экземпляров."""

from django.db import models


class Collection(models.Model):
    name = models.CharField("Название", max_length=255)
    records = models.ManyToManyField(
        "records.Record",
        through="CollectionRecord",
        related_name="collections",
        blank=True,
        verbose_name="Пластинки",
    )

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "коллекция"
        verbose_name_plural = "коллекции"

    def __str__(self):
        return self.name


class CollectionRecordQuerySet(models.QuerySet):
    """Повторно используемые выборки состояния пластинки в коллекции."""

    def current(self):
        """Экземпляры в коллекции, включая зарезервированные."""
        return self.filter(status__in=(
            self.model.Status.IN_COLLECTION,
            self.model.Status.RESERVED,
        ))

    def available(self):
        """Экземпляры, доступные для обмена (не резерв и не архив)."""
        return self.filter(status=self.model.Status.IN_COLLECTION)

    def reserved(self):
        return self.filter(status=self.model.Status.RESERVED)

    def removed(self):
        return self.filter(status=self.model.Status.REMOVED)

    def for_collection(self, collection):
        return self.filter(collection=collection)

    def for_record(self, record):
        return self.filter(record=record)

    def for_year(self, year):
        return self.filter(record__year=year)


class CollectionRecordManager(
    models.Manager.from_queryset(CollectionRecordQuerySet)
):
    """Менеджер для запросов к экземплярам в коллекциях."""


class CollectionRecord(models.Model):
    class Status(models.TextChoices):
        IN_COLLECTION = "in_collection", "В коллекции"
        RESERVED = "reserved", "Зарезервирована"
        REMOVED = "removed", "Выведена из коллекции"

    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="record_links",
        verbose_name="Коллекция",
    )
    record = models.ForeignKey(
        "records.Record",
        on_delete=models.CASCADE,
        related_name="collection_links",
        verbose_name="Пластинка",
    )
    status = models.CharField(
        "Состояние экземпляра",
        max_length=15,
        choices=Status.choices,
        default=Status.IN_COLLECTION,
        help_text=(
            "В коллекции — доступна; зарезервирована — не для обмена; "
            "выведена — сохранена только в истории."
        ),
    )

    objects = CollectionRecordManager()

    class Meta:
        ordering = ["collection_id", "record_id"]
        verbose_name = "пластинка в коллекции"
        verbose_name_plural = "пластинки в коллекциях"
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "record"],
                name="unique_collection_record",
            ),
        ]

    def __str__(self):
        return f"{self.collection}: {self.record}"
