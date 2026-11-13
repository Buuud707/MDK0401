from rest_framework import viewsets

from apps.accounts.permissions import OperatorWriteAuthenticatedRead
from apps.common import ProtectedDeleteMixin

from .models import Requester
from .serializers import RequesterSerializer


class RequesterViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Requester.objects.select_related("department")
    serializer_class = RequesterSerializer
    permission_classes = [OperatorWriteAuthenticatedRead]
    search_fields = ("full_name", "email", "phone")
    ordering_fields = ("full_name", "created_at")
