"""Общие вспомогательные классы для всех модулей."""
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class ProtectedDeleteMixin:
    """Вместо ошибки 500 возвращает 409, если запись нельзя удалить
    (на неё ссылаются другие данные, on_delete=PROTECT)."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Нельзя удалить: на запись ссылаются другие данные."},
                status=status.HTTP_409_CONFLICT,
            )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """Список основных эндпоинтов API."""
    def url(path):
        return request.build_absolute_uri(f"/api/{path}")

    return Response(
        {
            "auth_login": url("auth/login/"),
            "auth_refresh": url("auth/refresh/"),
            "me": url("auth/me/"),
            "users": url("users/"),
            "departments": url("departments/"),
            "categories": url("categories/"),
            "priorities": url("priorities/"),
            "requesters": url("requesters/"),
            "tickets": url("tickets/"),
            "reports_kpi": url("reports/kpi/"),
            "reports_export": url("reports/export/"),
        }
    )
