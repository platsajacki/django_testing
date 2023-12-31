from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse


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

    def test_comment_order(self, client, comments, news_pk):
        url = reverse(self.NEWS_DETAIL_PAGE, args=news_pk)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        all_comments = list(response.context['object'].comment_set.all())
        sorted_comments = sorted(all_comments, key=lambda x: x.created)
        assert all_comments == sorted_comments

    def test_form_not_available_anonymous_user(self, client, news_pk):
        url = reverse(self.NEWS_DETAIL_PAGE, args=news_pk)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert 'form' not in response.context
