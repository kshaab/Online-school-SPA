from typing import Any, Dict

from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from users.models import Payments, User


class PaymentsSerializer(ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"


class UserCreateSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "phone_number", "town")

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Создает пользователя."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class UserPublicSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "town", "avatar")


class UserPrivateSerializer(ModelSerializer):
    payments = SerializerMethodField()

    class Meta:
        model = User
        exclude = ("password",)

    def get_payments(self, obj: User) -> Payments:
        """Получает платежи пользователя."""
        queryset = Payments.objects.filter(user=obj)
        return PaymentsSerializer(queryset, many=True).data


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "town",
            "avatar",
            "first_name",
            "last_name",
        )
