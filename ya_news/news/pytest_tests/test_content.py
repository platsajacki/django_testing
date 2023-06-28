from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse

from news.models import Comment


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
class TestNewsContent:
    HOME_PAGE = reverse('news:home')

    def test_news_count(self, client):
        response = client.get(self.HOME_PAGE)
        assert response.status_code == HTTPStatus.OK
        object_list = response.context['object_list']
        assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client):
        response = client.get(self.HOME_PAGE)
        assert response.status_code == HTTPStatus.OK
        object_list = list(response.context['object_list'])
        sorted_objects = sorted(
            object_list, key=lambda x: x.date, reverse=True
        )
        assert object_list == sorted_objects


@pytest.mark.usefixtures('news')
@pytest.mark.django_db
class TestCommentContent:
    NEWS_DETAIL_PAGE = 'news:detail'

    @pytest.mark.usefixtures('comments')
    def test_comment_order(self):
        comments = list(Comment.objects.all())
        sorted_comments = sorted(comments, key=lambda x: x.created)
        assert comments == sorted_comments

    def test_form_not_available_anonymous_user(self, client, news_pk):
        url = reverse(self.NEWS_DETAIL_PAGE, args=news_pk)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert 'form' not in response.context
