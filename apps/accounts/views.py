from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdminRole
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Управление сотрудниками (только администратор)."""

    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    search_fields = ("username", "full_name", "email")
    ordering_fields = ("id", "username", "role")


class MeView(APIView):
    """Данные текущего пользователя."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)
