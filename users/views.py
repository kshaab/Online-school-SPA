from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from users.models import Payments, User
from users.permissions import IsOwnerOrReadOnly
from users.serializers import (PaymentsSerializer, UserCreateSerializer, UserPrivateSerializer, UserPublicSerializer,
                               UserUpdateSerializer)
from users.services import create_stripe_price, create_stripe_product, create_stripe_session, retrieve_stripe_session


@extend_schema(
    summary="Создание пользователя",
    description="Создает нового пользователя.",
    request=UserCreateSerializer,
    responses=UserPublicSerializer,
)
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer: Serializer) -> None:
        """Создает нового пользователя с хэшированным паролем и активирует его."""
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


@extend_schema(
    summary="Список пользователей",
    description="Возвращает список всех пользователей с публичными данными.",
    responses=UserPublicSerializer(many=True),
)
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    summary="Детали пользователя",
    description="Возвращает публичные данные пользователя. Если это текущий пользователь — приватные данные.",
    responses={200: UserPublicSerializer},
)
class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Получает сериалайзер для эндпоинта."""
        if self.get_object() == self.request.user:
            return UserPrivateSerializer
        return UserPublicSerializer


@extend_schema(
    summary="Обновление пользователя",
    description="Позволяет пользователю обновить свои данные.",
    request=UserUpdateSerializer,
    responses=UserPrivateSerializer,
)
class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


@extend_schema(
    summary="Удаление пользователя",
    description="Удаляет пользователя. Доступно только владельцу аккаунта.",
    responses=None,
)
class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


@extend_schema_view(
    create=extend_schema(
        summary="Создание платежа",
        description="Создает платеж и сессию stripe, если метод оплаты stripe.",
        request=PaymentsSerializer,
        responses=PaymentsSerializer,
    ),
    retrieve=extend_schema(
        summary="Детали платежа",
        description="Возвращает данные платежа и статус оплаты stripe.",
        responses=PaymentsSerializer,
    ),
    list=extend_schema(
        summary="Список платежей",
        description="Возвращает список всех платежей.",
    ),
    update=extend_schema(
        summary="Обновление платежа",
        description="Обновляет данные существующего платежа.",
        request=PaymentsSerializer,
        responses=PaymentsSerializer,
    ),
    partial_update=extend_schema(
        summary="Частичное обновление платежа",
        description="Частично обновляет данные платежа.",
        request=PaymentsSerializer,
        responses=PaymentsSerializer,
    ),
    destroy=extend_schema(
        summary="Удаление платежа",
        description="Удаляет платеж.",
        responses=None,
    ),
)
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

    def perform_create(self, serializer: Serializer) -> None:
        """Реализует оплату через страйп."""
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

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Проверяет статус оплаты в страйпе."""
        payment = self.get_object()
        paid = False
        if payment.payment_method == "stripe" and payment.stripe_session_id:
            session = retrieve_stripe_session(payment.stripe_session_id)
            if session and session.get("payment_status") == "paid":
                payment.is_paid = True
                payment.save()
                paid = True

        data = self.get_serializer(payment).data
        data["paid"] = paid
        return Response(data)
