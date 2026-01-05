from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from users.models import User


class CourseTestCase(APITestCase):

    def setUp(self):
        self.user = User(email="test@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.course = Course.objects.create(name="English", owner=self.user)
        self.client.force_authenticate(user=self.user)


    def test_course_retrieve(self):
        url = reverse("lms:course-detail", args=(self.course.id,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.course.name)


    def test_course_create(self):
        url = reverse("lms:course-list")
        data = {
            "name": "English",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)


    def test_course_update(self):
        url = reverse("lms:course-detail", args=(self.course.id,))
        data = {
            "name": "Math",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], "Math")


    def test_course_delete(self):
        url = reverse("lms:course-detail", args=(self.course.id,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)


    def test_course_list(self):
        url = reverse("lms:course-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': self.course.id,
                    'is_subscribe': False,
                    'lessons': [],
                    'name': self.course.name,
                    'preview': None,
                    'description': None,
                    'owner': self.course.owner.id
                }
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User(email="test@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.course = Course.objects.create(name="English")
        self.lesson = Lesson.objects.create(name="Alphabet", course=self.course, owner=self.user)
        self.client.force_authenticate(user=self.user)


    def test_lesson_retrieve(self):
        url = reverse("lms:lesson-retrieve", args=(self.lesson.id,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.lesson.name)


    def test_lesson_create(self):
        url = reverse("lms:lesson-create")
        data = {
            "name": "Alphabet",
            "course": self.course.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)


    def test_lesson_update(self):
        url = reverse("lms:lesson-update", args=(self.lesson.id,))
        data = {
            "name": "Subtraction",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], "Subtraction")


    def test_lesson_delete(self):
        url = reverse("lms:lesson-delete", args=(self.lesson.id,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)


    def test_lesson_list(self):
        url = reverse("lms:lesson-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': self.lesson.id,
                    'name': self.lesson.name,
                    'description': None,
                    'course': self.course.id,
                    'owner': self.lesson.owner.id
                }
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User(email="test@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.course = Course.objects.create(name="English", owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_subscription_create(self):
        url = reverse("lms:subscriptions")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(owner=self.user, course=self.course).exists())


    def test_subscription_delete(self):
        Subscription.objects.create(owner=self.user, course=self.course)
        url = reverse("lms:subscriptions")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 0)





