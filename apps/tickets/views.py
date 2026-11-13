from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminRole, OperatorWriteAuthenticatedRead

from .models import Ticket, TicketError
from .serializers import (
    AssignSerializer, CommentSerializer, StatusChangeSerializer,
    TicketDetailSerializer, TicketSerializer,
)


class TicketViewSet(viewsets.ModelViewSet):
    """Обращения: список, карточка, создание, смена статуса, назначение, комментарии.

    Фильтры списка (query-параметры): status, category, priority, requester,
    assignee (id или me), overdue=1, а также search и ordering.
    """

    queryset = Ticket.objects.select_related(
        "requester", "category", "priority", "assignee", "created_by"
    )
    serializer_class = TicketSerializer
    search_fields = ("title", "description", "requester__full_name")
    ordering_fields = ("created_at", "due_at", "priority__level", "status")

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminRole()]
        return [OperatorWriteAuthenticatedRead()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action != "list":
            return qs
        params = self.request.query_params
        for field in ("status", "category", "priority", "requester"):
            value = params.get(field)
            if value:
                if field == "status":
                    qs = qs.filter(status=value)
                elif value.isdigit():
                    qs = qs.filter(**{f"{field}_id": int(value)})
        assignee = params.get("assignee")
        if assignee == "me":
            qs = qs.filter(assignee=self.request.user)
        elif assignee and assignee.isdigit():
            qs = qs.filter(assignee_id=int(assignee))
        if params.get("overdue") in ("1", "true", "True"):
            qs = qs.filter(due_at__lt=timezone.now()).exclude(status__in=Ticket.FINAL_STATUSES)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _detail(self, ticket):
        ticket = Ticket.objects.get(pk=ticket.pk)  # свежие данные
        return TicketDetailSerializer(ticket, context=self.get_serializer_context()).data

    @action(detail=True, methods=["post"], url_path="status")
    def set_status(self, request, pk=None):
        """POST {"status": "...", "note": "..."} — сменить статус."""
        ticket = self.get_object()
        ser = StatusChangeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            ticket.change_status(ser.validated_data["status"], request.user, ser.validated_data["note"])
        except TicketError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self._detail(ticket))

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        """POST {"assignee": id} — назначить исполнителя (без id — на себя)."""
        ticket = self.get_object()
        ser = AssignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        assignee = ser.validated_data.get("assignee") or request.user
        try:
            ticket.assign(assignee, by=request.user)
        except TicketError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self._detail(ticket))

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == "GET":
            data = CommentSerializer(ticket.comments.select_related("author"), many=True).data
            return Response(data)
        ser = CommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(ticket=ticket, author=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)
