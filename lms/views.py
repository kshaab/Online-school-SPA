from datetime import timedelta
from typing import List, Type

from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson, Subscription
from lms.paginators import CustomPagination
from lms.serializers import CourseDetailSerializer, CourseSerializer, LessonSerializer, SubscriptionSerializer
from lms.tasks import send_info_about_updates
from users.permissions import IsModer, IsOwner


@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Возвращает список всех курсов с пагинацией.",
    ),
    retrieve=extend_schema(
        summary="Детали курса",
        description="Возвращает детальную информацию о курсе по ID.",
        responses=CourseDetailSerializer,
    ),
    create=extend_schema(
        summary="Создание курса",
        description="Создаёт новый курс и привязывает его к текущему пользователю.",
        request=CourseSerializer,
        responses=CourseSerializer,
    ),
    update=extend_schema(
        summary="Обновление курса",
        description="Обновляет данные существующего курса.",
        request=CourseSerializer,
        responses=CourseSerializer,
    ),
    partial_update=extend_schema(
        summary="Частичное обновление курса",
        description="Частично обновляет данные курса.",
        request=CourseSerializer,
        responses=CourseSerializer,
    ),
    destroy=extend_schema(
        summary="Удаление курса",
        description="Удаляет курс, если текущий пользователь является владельцем.",
        responses=None,
    ),
)
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all().order_by("id")
    pagination_class = CustomPagination

    def get_serializer_class(self) -> Type[Serializer]:
        """Получает сериализатор для текущего действия."""
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """Получает права доступа для эндпоинтов."""
        user = self.request.user
        if self.action == "create":
            if user.groups.filter(name="Модераторы").exists():
                self.permission_classes = []
            else:
                self.permission_classes = [IsAuthenticated]
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = [IsModer | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer: Serializer) -> None:
        """Привязывает курс к пользователю."""
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def perform_update(self, serializer: Serializer) -> None:
        """Проверяет обновления курса и отправляет письмо при наличии обновлений"""
        course = self.get_object()
        last_update = course.updated_at
        serializer.save()

        if last_update and now() - last_update >= timedelta(hours=4):
            send_info_about_updates.delay(course.id)


@extend_schema(
    summary="Создание урока",
    description="Создает новый урок и привязывает его к текущему пользователю.",
    request=LessonSerializer,
    responses=LessonSerializer,
)
class LessonCreateApiView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """Получает права доступа для эндпоинтов."""
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            self.permission_classes = []
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer) -> None:
        """Привязывает урок к пользователю"""
        serializer.save(owner=self.request.user)


@extend_schema(
    summary="Список уроков",
    description="Возвращает список всех уроков с пагинацией.",
    responses=LessonSerializer(many=True),
)
class LessonListApiView(generics.ListAPIView):
    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


@extend_schema(
    summary="Детали урока",
    description="Возвращает детальную информацию об уроке по ID.",
    responses=LessonSerializer,
)
class LessonRetrieveApiView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner | IsModer]


@extend_schema(
    summary="Обновление урока",
    description="Обновляет существующий урок. Только владелец или модератор.",
    request=LessonSerializer,
    responses=LessonSerializer,
)
class LessonUpdateApiView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner | IsModer]

    def perform_update(self, serializer: Serializer) -> None:
        """Проверяет обновления уроков в курсе и отправляет уведомление при наличии"""
        lesson = self.get_object()
        course = lesson.course

        last_update = course.updated_at

        serializer.save()

        if last_update and now() - last_update >= timedelta(hours=4):
            send_info_about_updates.delay(course.id)


@extend_schema(
    summary="Удаление урока",
    description="Удаляет урок. Только владелец или модератор.",
    responses=None,
)
class LessonDestroyApiView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """Получает права доступа для эндпоинтов."""
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            self.permission_classes = []
        else:
            self.permission_classes = [IsOwner]
        return super().get_permissions()


@extend_schema(
    summary="Создание/удаление подписки",
    description="Если подписка существует – удаляет её. Если нет – создаёт подписку на курс.",
    request=SubscriptionSerializer,
    responses={200: {"message": "Подписка удалена"}, 201: {"message": "Подписка добавлена"}},
)
class SubscriptionCreateApiView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer

    def post(self, request, *args, **kwargs) -> Response:
        """Удаляет и создает подписку на курс у пользователя"""
        user = request.user
        course_id = request.data.get("course_id")
        course_item = Course.objects.get(id=course_id)
        subs_item = Subscription.objects.filter(course=course_item, owner=user)
        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            Subscription.objects.create(owner=user, course=course_item)
            message = "Подписка добавлена"
            return Response({"message": message}, status=status.HTTP_201_CREATED)
