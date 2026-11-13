from rest_framework import viewsets

from apps.accounts.permissions import AdminWriteAuthenticatedRead
from apps.common import ProtectedDeleteMixin

from .models import Category, Department, Priority
from .serializers import CategorySerializer, DepartmentSerializer, PrioritySerializer


class CatalogViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """Базовый класс справочника: читают все, меняет администратор."""

    permission_classes = [AdminWriteAuthenticatedRead]
    search_fields = ("name",)


class DepartmentViewSet(CatalogViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CategoryViewSet(CatalogViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PriorityViewSet(CatalogViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
