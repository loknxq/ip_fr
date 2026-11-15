"""Коллекции и явная таблица связи с пластинками."""

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


class CollectionRecord(models.Model):
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
