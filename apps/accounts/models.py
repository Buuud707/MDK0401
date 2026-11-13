from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Сотрудник IT-отдела / руководитель / администратор."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        OPERATOR = "operator", "Оператор поддержки"
        MANAGER = "manager", "Руководитель"

    full_name = models.CharField("ФИО", max_length=255, blank=True)
    role = models.CharField(
        "Роль",
        max_length=32,
        choices=Role.choices,
        default=Role.OPERATOR,
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name or self.username
