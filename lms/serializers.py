from typing import Dict, List

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from lms.models import Course, Lesson, Subscription
from lms.validators import LinkValidator


class CourseSerializer(ModelSerializer):
    is_subscribe = SerializerMethodField()
    lessons = SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"
        exclude = ("updated_at",)

    def get_lessons(self, obj: Course) -> List[Dict]:
        """Возвращает список уроков для курса."""
        queryset = obj.lesson_set.all()
        return LessonSerializer(queryset, many=True).data

    def get_is_subscribe(self, obj: Course) -> bool:
        """Проверяет есть ли подписка у пользователя."""
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(owner=user, course=obj).exists()


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "name", "description", "course", "owner")
        validators = [LinkValidator(field="video_link")]


class CourseDetailSerializer(ModelSerializer):
    count_lessons = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("name", "count_lessons", "lessons")

    def get_count_lessons(self, obj: Course) -> int:
        """Считает количество уроков в курсе."""
        return obj.lesson_set.count()


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
