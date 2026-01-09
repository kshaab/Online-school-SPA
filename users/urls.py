from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (PaymentsViewSet, UserCreateAPIView, UserDestroyAPIView, UserListAPIView, UserRetrieveAPIView,
                         UserUpdateAPIView)

app_name = UsersConfig.name
router = DefaultRouter()
router.register("payments", PaymentsViewSet)

urlpatterns = router.urls + [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("user/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("user/<int:pk>/", UserRetrieveAPIView.as_view(), name="user-retrieve"),
    path("user/<int:pk>/delete", UserDestroyAPIView.as_view(), name="user-delete"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
