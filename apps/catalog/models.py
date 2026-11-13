from django.db import models


class Department(models.Model):
    name = models.CharField("Название", max_length=255, unique=True)

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Название", max_length=255, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Priority(models.Model):
    """Приоритет обращения. От него зависит срок решения (SLA)."""

    name = models.CharField("Название", max_length=100, unique=True)
    level = models.PositiveSmallIntegerField("Уровень (больше — важнее)", unique=True)
    sla_hours = models.PositiveIntegerField("Срок решения, часов", default=24)

    class Meta:
        verbose_name = "Приоритет"
        verbose_name_plural = "Приоритеты"
        ordering = ["-level"]

    def __str__(self):
        return self.name
