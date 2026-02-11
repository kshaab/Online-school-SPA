from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey

from lms.models import Course, Lesson


class User(AbstractUser):
    """Модель пользователя"""
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)
    town = models.CharField(max_length=35, verbose_name="Город", blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payments(models.Model):
    """Модель платежей"""
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличными"),
        ("credit_card", "Перевод на счет"),
        ("stripe", "Stripe"),
    ]
    user = ForeignKey(to=User, verbose_name="Плательщик", on_delete=models.SET_NULL, null=True)
    payment_date = models.DateField(verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        to=Course, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Оплаченный курс"
    )
    paid_lesson = models.ForeignKey(
        to=Lesson, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Оплаченный урок"
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(max_length=20, verbose_name="Способ оплаты", choices=PAYMENT_METHOD_CHOICES)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID сессии")
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_link = models.URLField(max_length=2000, blank=True, null=True, verbose_name="Ссылка на оплату")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"{self.user} – {self.payment_amount}"
