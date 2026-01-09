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

    def get_lessons(self, obj):
        queryset = obj.lesson_set.all()
        return LessonSerializer(queryset, many=True).data

    def get_is_subscribe(self, obj):
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

    def get_count_lessons(self, obj):
        return obj.lesson_set.count()


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"