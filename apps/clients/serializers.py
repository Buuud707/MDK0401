from rest_framework import serializers

from .models import Requester


class RequesterSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField(label="Подразделение")

    class Meta:
        model = Requester
        fields = (
            "id", "full_name", "email", "phone", "position",
            "department", "department_name", "created_at",
        )
        read_only_fields = ("created_at",)
        extra_kwargs = {
            "id": {"label": "Номер"},
            "full_name": {"label": "ФИО заявителя"},
            "email": {"label": "Электронная почта"},
            "phone": {"label": "Телефон"},
            "position": {"label": "Должность"},
            "department": {"label": "Подразделение"},
            "created_at": {"label": "Дата создания"},
        }

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
