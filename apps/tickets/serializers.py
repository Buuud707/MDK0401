from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import StatusLog, Ticket, TicketComment

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField(label="Автор")

    class Meta:
        model = TicketComment
        fields = ("id", "author", "author_name", "text", "created_at")
        read_only_fields = ("author", "created_at")
        extra_kwargs = {
            "id": {"label": "Номер"},
            "author": {"label": "Автор"},
            "text": {"label": "Комментарий"},
            "created_at": {"label": "Дата создания"},
        }

    def get_author_name(self, obj):
        return str(obj.author) if obj.author else None


class StatusLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField(label="Кто изменил")

    class Meta:
        model = StatusLog
        fields = ("id", "old_status", "new_status", "changed_by_name", "note", "changed_at")
        extra_kwargs = {
            "id": {"label": "Номер"},
            "old_status": {"label": "Предыдущий статус"},
            "new_status": {"label": "Новый статус"},
            "note": {"label": "Примечание"},
            "changed_at": {"label": "Дата изменения"},
        }

    def get_changed_by_name(self, obj):
        return str(obj.changed_by) if obj.changed_by else None


class TicketSerializer(serializers.ModelSerializer):
    number = serializers.CharField(label="Номер обращения", read_only=True)
    is_overdue = serializers.BooleanField(label="Просрочено", read_only=True)
    status_display = serializers.CharField(source="get_status_display", label="Название статуса", read_only=True)
    requester_name = serializers.CharField(source="requester.full_name", label="ФИО заявителя", read_only=True)
    category_name = serializers.CharField(source="category.name", label="Категория", read_only=True)
    priority_name = serializers.CharField(source="priority.name", label="Приоритет", read_only=True)
    assignee_name = serializers.SerializerMethodField(label="Исполнитель")

    class Meta:
        model = Ticket
        fields = (
            "id", "number", "title", "description",
            "requester", "requester_name", "category", "category_name",
            "priority", "priority_name", "status", "status_display",
            "assignee", "assignee_name", "created_by",
            "created_at", "updated_at", "due_at", "resolved_at", "is_overdue",
        )
        read_only_fields = (
            "status", "assignee", "created_by",
            "created_at", "updated_at", "due_at", "resolved_at",
        )
        extra_kwargs = {
            "id": {"label": "Номер записи"},
            "title": {"label": "Тема обращения"},
            "description": {"label": "Описание"},
            "requester": {"label": "Заявитель"},
            "category": {"label": "Категория"},
            "priority": {"label": "Приоритет"},
            "status": {"label": "Статус"},
            "assignee": {"label": "Исполнитель"},
            "created_by": {"label": "Кто зарегистрировал"},
            "created_at": {"label": "Дата создания"},
            "updated_at": {"label": "Дата обновления"},
            "due_at": {"label": "Срок решения"},
            "resolved_at": {"label": "Дата решения"},
        }

    def get_assignee_name(self, obj):
        return str(obj.assignee) if obj.assignee else None


class TicketDetailSerializer(TicketSerializer):
    comments = CommentSerializer(many=True, read_only=True, label="Комментарии")
    history = StatusLogSerializer(source="logs", many=True, read_only=True, label="История статусов")

    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ("comments", "history")


class StatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(label="Новый статус", choices=Ticket.Status.choices)
    note = serializers.CharField(label="Примечание", required=False, allow_blank=True, max_length=255, default="")


class AssignSerializer(serializers.Serializer):
    assignee = serializers.PrimaryKeyRelatedField(
        label="Исполнитель",
        queryset=User.objects.filter(is_active=True),
        required=False,
    )
