from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Модераторы")
        permissions = Permission.objects.filter(
            codename__in=[
                "view_course",
                "change_course",
                "view_lesson",
                "change_lesson",
            ]
        )
        group.permissions.add(*permissions)
        self.stdout.write(self.style.SUCCESS("The group 'Модераторы' was successfully created"))
