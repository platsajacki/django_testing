from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note

User = get_user_model()


class TestRoutes(TestCase):
    TITLE = 'Заметка'
    TEXT = 'Текст'
    SLUG = 'note'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, slug=cls.SLUG, author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            'notes:home', 'users:login', 'users:logout', 'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_auth(self):
        urls = (
            'notes:add', 'notes:list', 'notes:success'
        )
        self.client.force_login(self.author)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        names_args = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', self.note.slug),
            ('notes:detail', self.note.slug),
            ('notes:delete', self.note.slug)
        )
        login_url = reverse('users:login')
        for name, arg in names_args:
            with self.subTest(name=name, arg=arg):
                if arg is None:
                    url = reverse(name, arg)
                else:
                    url = reverse(name, args=(arg,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
