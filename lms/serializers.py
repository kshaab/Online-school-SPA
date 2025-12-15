from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from lms.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    lessons = SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons(self, obj):
        queryset = obj.lessons.all()
        return LessonSerializer(queryset, many=True).data


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "name", "description")


class CourseDetailSerializer(ModelSerializer):
    count_lessons = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("name", "count_lessons", "lessons")

    def get_count_lessons(self, obj):
        return obj.lessons.count()
