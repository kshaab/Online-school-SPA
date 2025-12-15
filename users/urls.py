from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

from users.apps import UsersConfig

app_name = UsersConfig
router = DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = router.urls
