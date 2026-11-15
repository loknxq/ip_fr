"""Пользователь предметной области ПР7, не учётная запись Django Auth."""

from django.db import models


class User(models.Model):
    name = models.CharField("Имя", max_length=255)
    email = models.EmailField("Электронная почта", max_length=254)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "пользователь сервиса"
        verbose_name_plural = "пользователи сервиса"

    def __str__(self):
        return f"{self.name} <{self.email}>"
