from rest_framework import serializers

from .models import Category, Department, Priority


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name")
        extra_kwargs = {
            "id": {"label": "Номер"},
            "name": {"label": "Название подразделения"},
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        extra_kwargs = {
            "id": {"label": "Номер"},
            "name": {"label": "Название категории"},
        }


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ("id", "name", "level", "sla_hours")
        extra_kwargs = {
            "id": {"label": "Номер"},
            "name": {"label": "Название приоритета"},
            "level": {"label": "Уровень важности"},
            "sla_hours": {"label": "Срок решения, часов"},
        }
