from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class TicketError(Exception):
    """Нарушение бизнес-правил (недопустимый переход статуса и т.п.)."""


class Ticket(models.Model):
    """Обращение пользователя в службу поддержки."""

    class Status(models.TextChoices):
        NEW = "new", "Новое"
        IN_PROGRESS = "in_progress", "В работе"
        WAITING = "waiting", "Ожидает ответа"
        RESOLVED = "resolved", "Решено"
        CLOSED = "closed", "Закрыто"

    TRANSITIONS = {
        "new": ["in_progress", "closed"],
        "in_progress": ["waiting", "resolved"],
        "waiting": ["in_progress", "resolved"],
        "resolved": ["closed", "in_progress"],
        "closed": [],
    }
    FINAL_STATUSES = ("resolved", "closed")

    title = models.CharField("Тема", max_length=255)
    description = models.TextField("Описание", blank=True)
    requester = models.ForeignKey(
        "clients.Requester", verbose_name="Заявитель",
        on_delete=models.PROTECT, related_name="tickets",
    )
    category = models.ForeignKey(
        "catalog.Category", verbose_name="Категория", on_delete=models.PROTECT,
    )
    priority = models.ForeignKey(
        "catalog.Priority", verbose_name="Приоритет", on_delete=models.PROTECT,
    )
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Исполнитель",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Зарегистрировал",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tickets",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    due_at = models.DateTimeField("Срок решения", null=True, blank=True)
    resolved_at = models.DateTimeField("Решено", null=True, blank=True)

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} {self.title}"

    @property
    def number(self):
        return f"REQ-{self.pk:06d}" if self.pk else ""

    @property
    def is_overdue(self):
        return (
            self.status not in self.FINAL_STATUSES
            and self.due_at is not None
            and self.due_at < timezone.now()
        )

    def save(self, *args, **kwargs):
        if not self.due_at:
            self.due_at = timezone.now() + timedelta(hours=self.priority.sla_hours)
        if self.status in self.FINAL_STATUSES:
            if not self.resolved_at:
                self.resolved_at = timezone.now()
        else:
            self.resolved_at = None
        super().save(*args, **kwargs)

    def change_status(self, new_status, user=None, note=""):
        """Смена статуса с проверкой допустимости и записью в журнал."""
        allowed = self.TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            labels = dict(self.Status.choices)
            raise TicketError(
                f"Переход «{labels.get(self.status, self.status)}» → "
                f"«{labels.get(new_status, new_status)}» недопустим"
            )
        old = self.status
        with transaction.atomic():
            self.status = new_status
            self.save()
            StatusLog.objects.create(
                ticket=self, old_status=old, new_status=new_status,
                changed_by=user, note=note,
            )

    def assign(self, assignee, by=None):
        """Назначение исполнителя. Новое обращение переходит «В работу»."""
        if self.status == self.Status.CLOSED:
            raise TicketError("Обращение закрыто, назначить исполнителя нельзя")
        if not (assignee.is_superuser or assignee.role in ("admin", "operator")):
            raise TicketError("Исполнитель должен быть оператором или администратором")
        with transaction.atomic():
            self.assignee = assignee
            self.save()
            if self.status == self.Status.NEW:
                self.change_status("in_progress", by, f"Назначен исполнитель: {assignee}")


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Автор",
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    text = models.TextField("Текст")
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий к {self.ticket_id}"


class StatusLog(models.Model):
    """Журнал изменения статусов — единая история обращения."""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="logs")
    old_status = models.CharField("Был", max_length=20, choices=Ticket.Status.choices)
    new_status = models.CharField("Стал", max_length=20, choices=Ticket.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Кто изменил",
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    changed_at = models.DateTimeField("Когда", auto_now_add=True)
    note = models.CharField("Примечание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Запись журнала"
        verbose_name_plural = "Журнал статусов"
        ordering = ["changed_at", "id"]

    def __str__(self):
        return f"{self.ticket_id}: {self.old_status} → {self.new_status}"
