from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
class TestCommentLogic:
    NEWS_DETAIL_PAGE = 'news:detail'

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('client'), False),
            (pytest.lazy_fixture('author_client'), True)
        ),
    )
    def test_create_comment(
            self, parametrized_client, expected_status, form_data, news_pk
    ):
        url = reverse(self.NEWS_DETAIL_PAGE, args=news_pk)
        before = Comment.objects.count()
        parametrized_client.post(url, data=form_data)
        after = Comment.objects.count()
        assert (before != after) == expected_status

    def test_user_cant_use_bad_words(self, author_client, news_pk):
        url = reverse(self.NEWS_DETAIL_PAGE, args=news_pk)
        bad_words_data = {'text': f'Очень плохое слово - {BAD_WORDS[0]}'}
        response = author_client.post(url, data=bad_words_data)
        assert Comment.objects.count() == 0
        assert 'form' in response.context
        form = response.context['form']
        assert 'text' in form.errors
        assert WARNING in form.errors['text']

    class TestCommentEdit:
        COMMENT_EDIT_PAGE = 'news:edit'

        def test_author_can_edit_comment(
                self, author_client, form_data, comment, comment_pk
        ):
            url = reverse(self.COMMENT_EDIT_PAGE, args=comment_pk)
            response = author_client.post(url, data=form_data)
            assert response.status_code == HTTPStatus.FOUND
            comment.refresh_from_db()
            assert comment.text == form_data['text']

        def test_other_user_cant_edit_comment(
                self, admin_client, form_data, comment, comment_pk
        ):
            url = reverse(self.COMMENT_EDIT_PAGE, args=comment_pk)
            response = admin_client.post(url, data=form_data)
            assert response.status_code == HTTPStatus.NOT_FOUND
            comment_from_db = Comment.objects.get(id=comment.id)
            assert comment.text == comment_from_db.text

    @pytest.mark.usefixtures('comment')
    class TestCommentEditDelete:
        COMMENT_DELLETE_PAGE = 'news:delete'

        def test_author_can_delete_comment(self, author_client, comment_pk):
            url = reverse(self.COMMENT_DELLETE_PAGE, args=comment_pk)
            response = author_client.post(url)
            assert response.status_code == HTTPStatus.FOUND
            assert Comment.objects.count() == 0

        def test_other_user_cant_delete_comment(
                self, admin_client, comment_pk
        ):
            url = reverse(self.COMMENT_DELLETE_PAGE, args=comment_pk)
            response = admin_client.post(url)
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert Comment.objects.count() == 1
