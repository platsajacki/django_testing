from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Note

User = get_user_model()


class TestContent(TestCase):
    NOTES_LIST = reverse('notes:list')
    ADD_NOTE_PAGE = reverse('notes:add')

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
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_list_of_notes(self):
        response = self.client_author.get(self.NOTES_LIST)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note, response.context['object_list'])

    def test_elses_note_in_list_of_notes(self):
        response = self.client_reader.get(self.NOTES_LIST)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_authorized_client_has_form(self):
        for url in (self.ADD_NOTE_PAGE, self.edit_url):
            with self.subTest(name=url):
                response = self.client_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIn('form', response.context)
