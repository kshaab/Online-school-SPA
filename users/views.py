from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.models import Payments, User
from users.permissions import IsOwnerOrReadOnly
from users.serializers import (PaymentsSerializer, UserCreateSerializer, UserPrivateSerializer, UserPublicSerializer,
                               UserUpdateSerializer)
from users.services import create_stripe_price, create_stripe_session, create_stripe_product


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.get_object() == self.request.user:
            return UserPrivateSerializer
        return UserPublicSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class PaymentsViewSet(ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ("payment_date",)
    filterset_fields = (
        "paid_course",
        "paid_lesson",
        "payment_method",
    )

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        if payment.payment_method == "stripe":
            amount = payment.payment_amount
            product_name = payment.paid_course.name
            product = create_stripe_product(product_name)
            price = create_stripe_price(payment_amount=amount, product_id=product["id"])
            session_id, payment_link = create_stripe_session(price["id"])
            payment.stripe_session_id = session_id
            payment.stripe_link = payment_link
            payment.save()

