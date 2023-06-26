from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now

from news.models import Comment


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
class TestNewsContent:
    HOME_PAGE = reverse('news:home')

    def test_news_count(self, client):
        object_list = client.get(self.HOME_PAGE).context['object_list']
        assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client):
        object_list = client.get(self.HOME_PAGE).context['object_list']
        assert object_list[0].date > object_list[1].date


@pytest.mark.usefixtures('news')
@pytest.mark.django_db
class TestCommentContent:
    NEWS_DETAIL_PAGE = 'news:detail'

    def test_comment_order(self, news, author):
        comments = [
            Comment(
                news=news,
                author=author,
                text='Текст комментария',
                created=now() - timedelta(days=index)
            ) for index in range(2)
        ]
        Comment.objects.bulk_create(comments)
        two_comments = Comment.objects.all()
        assert two_comments[0].created < two_comments[1].created

    def test_form_not_available_anonymous_user(self, client, news_pk):
        url = reverse(self.NEWS_DETAIL_PAGE, args=news_pk)
        context = client.get(url).context
        assert 'form' not in context
