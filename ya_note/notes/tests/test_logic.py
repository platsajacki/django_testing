from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Note

User = get_user_model()


class TestContent(TestCase):
    ADD_NOTE_PAGE = reverse('notes:add')
    DONE_PAGE = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заметка', text='Текст', slug='note', author=cls.author
        )
        cls.note_without_slug = Note.objects.create(
            title='Заметка', text='Текст', author=cls.author
        )
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст',
            'slug': 'note2'
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.note_with_non_unique_slug = Note.objects.create(
                title='Заметка', text='Текст',
                slug='note', author=self.author
            )

    def test_anonymous_user_cant_create_note(self):
        before_count_note = Note.objects.count()
        response = self.client.post(self.ADD_NOTE_PAGE, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        after_count_note = Note.objects.count()
        self.assertEqual(before_count_note, after_count_note)

    def test_auth_user_can_create_note(self):
        before_count_note = Note.objects.count()
        response = self.client_author.post(
            self.ADD_NOTE_PAGE, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        after_count_note = Note.objects.count() - 1
        self.assertEqual(before_count_note, after_count_note)

    def test_user_can_edit_their_notes(self):
        response = self.client_author.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.DONE_PAGE)

    def test_user_can_delete_their_notes(self):
        response = self.client_author.delete(self.delete_url)
        self.assertRedirects(response, self.DONE_PAGE)

    def test_reader_can_edit_their_notes(self):
        response = self.client_reader.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_reader_can_edit_their_notes(self):
        response = self.client_reader.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
