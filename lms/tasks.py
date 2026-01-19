from celery import shared_task
from django.core.mail import send_mail

from lms.models import Subscription
from online_school import settings


@shared_task
def send_info_about_updates(course_id):
    """Отправляет письмо об обновлении курса"""
    subscription = Subscription.objects.filter(id=course_id)

    for sub in subscription:
        send_mail(
            subject="Обновления курса",
            message="В ваш курс по подписке добавлены новые материалы!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.owner.email],
            fail_silently=True,
        )
