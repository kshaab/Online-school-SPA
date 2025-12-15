from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from users.models import Payments, User


class PaymentsSerializer(ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"


class UserSerializer(ModelSerializer):
    payments = SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "phone_number", "town", "avatar", "payments")

    def get_payments(self, obj):
        queryset = Payments.objects.filter(user=obj)
        return PaymentsSerializer(queryset, many=True).data
