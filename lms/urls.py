from django.urls import path
from rest_framework.routers import SimpleRouter

from lms.apps import LmsConfig
from lms.views import (CourseViewSet, LessonCreateApiView, LessonDestroyApiView, LessonListApiView,
                       LessonRetrieveApiView, LessonUpdateApiView)

app_name = LmsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lesson/create/", LessonCreateApiView.as_view(), name="lesson_create"),
    path("lesson/list/", LessonListApiView.as_view(), name="lesson_list"),
    path("lesson/<int:pk>/", LessonRetrieveApiView.as_view(), name="lesson_retrieve"),
    path("lesson/<int:pk>/update", LessonUpdateApiView.as_view(), name="lesson_update"),
    path("lesson/<int:pk>/delete", LessonDestroyApiView.as_view(), name="lesson_delete"),
]

urlpatterns += router.urls
