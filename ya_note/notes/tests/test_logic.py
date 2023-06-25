from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from ..models import Note

User = get_user_model()


class TestContent(TestCase):
    TITLE = 'Заметка'
    TEXT = 'Текст'
    SLUG = 'note'
    SLUG2 = 'note2'
    ADD_NOTE_PAGE = reverse('notes:add')
    DONE_PAGE = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.another_user = User.objects.create(username='Пользователь')
        cls.client_another_user = Client()
        cls.client_another_user.force_login(cls.another_user)
        cls.note_author = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, slug=cls.SLUG, author=cls.author
        )
        cls.note_without_slug = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, author=cls.author
        )
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG2
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note_author.slug,))

    def test_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.note_with_non_unique_slug = Note.objects.create(
                title=self.TITLE, text=self.TEXT,
                slug=self.SLUG, author=self.author
            )

    def test_anonymous_user_cant_create_note(self):
        before_count_note = Note.objects.count()
        self.client.post(self.ADD_NOTE_PAGE, data=self.form_data)
        after_count_note = Note.objects.count()
        self.assertEqual(before_count_note, after_count_note)

    def test_auth_user_can_create_note(self):
        before_count_note = Note.objects.count()
        self.client_author.post(self.ADD_NOTE_PAGE, data=self.form_data)
        after_count_note = Note.objects.count() - 1
        self.assertEqual(before_count_note, after_count_note)

    def test_unique_slug(self):
        translit = slugify(self.TITLE)
        self.assertEqual(translit, self.note_without_slug.slug)

    def test_user_can_edit_their_notes(self):
        response = self.client_author.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.DONE_PAGE)

    def test_user_can_delete_their_notes(self):
        response = self.client_author.delete(self.delete_url)
        self.assertRedirects(response, self.DONE_PAGE)

    def test_another_user_can_edit_their_notes(self):
        response = self.client_another_user.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_another_user_can_edit_their_notes(self):
        response = self.client_another_user.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
