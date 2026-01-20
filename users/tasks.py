from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from users.models import User


@shared_task
def block_inactive_user():
    """Блокирует неактивных пользователей после месяца неактива"""
    last_login = now() - timedelta(days=30)
    inactive_user = User.objects.filter(is_active=True, last_login__lt=last_login)
    inactive_user.update(is_active=False)
