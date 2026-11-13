from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(label="Пароль", write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "email", "role", "is_active", "password")
        extra_kwargs = {
            "id": {"label": "Номер"},
            "username": {"label": "Логин"},
            "full_name": {"label": "ФИО"},
            "email": {"label": "Электронная почта"},
            "role": {"label": "Роль"},
            "is_active": {"label": "Учётная запись активна"},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Обязательное поле."})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
