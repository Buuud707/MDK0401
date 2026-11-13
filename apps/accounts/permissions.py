from rest_framework.permissions import SAFE_METHODS, BasePermission


def has_role(user, *roles):
    """Проверяет вход пользователя и его роль."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.role in roles


class IsAdminRole(BasePermission):
    """Только администратор."""

    def has_permission(self, request, view):
        return has_role(request.user, "admin")


class AdminWriteAuthenticatedRead(BasePermission):
    """Читать могут все вошедшие, изменять — только администратор (справочники)."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return has_role(request.user, "admin")


class OperatorWriteAuthenticatedRead(BasePermission):
    """Читать могут все вошедшие (в т.ч. руководитель),
    изменять — администратор и оператор."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return has_role(request.user, "admin", "operator")
