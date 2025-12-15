from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentsViewSet

app_name = "users"
router = DefaultRouter()
router.register("users", UserViewSet)
router.register("payments", PaymentsViewSet)
urlpatterns = router.urls
