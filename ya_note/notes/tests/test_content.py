from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note

User = get_user_model()


class TestContent(TestCase):
    NOTES_LIST = reverse('notes:list')
    ADD_NOTE_PAGE = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заметка', text='Текст', slug='note', author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_list_of_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST)
        self.assertIn(self.note, response.context['object_list'])

    def test_elses_note_in_list_of_notes(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTES_LIST)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for url in (self.ADD_NOTE_PAGE, self.edit_url):
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
