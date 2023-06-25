from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note

User = get_user_model()


class TestContent(TestCase):
    TITLE = 'Заметка'
    TEXT = 'Текст'
    SLUG = 'note'
    SLUG2 = 'note2'
    NOTES_LIST = reverse('notes:list')
    ADD_NOTE_PAGE = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_user = User.objects.create(username='Пользователь')
        cls.note_author = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, slug=cls.SLUG, author=cls.author
        )
        cls.note_user = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT,
            slug=cls.SLUG2, author=cls.another_user
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))

    def test_note_in_list_of_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST)
        self.assertIn(self.note_author, response.context['object_list'])

    def test_elses_note_in_list_of_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST)
        self.assertNotIn(self.note_user, response.context['object_list'])

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for url in (self.ADD_NOTE_PAGE, self.edit_url):
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
