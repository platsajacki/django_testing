from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_pk'))
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk'))
    )
)
class TestEditDelete:
    @pytest.mark.django_db
    def test_anonymous_user_cant_edit_and_delete_comment(
            self, client, name, args
    ):
        url = reverse(name, args=args)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        response = client.get(url)
        assertRedirects(response, expected_url)

    @pytest.mark.parametrize(
        ('parametrized_client, expected_status'),
        (
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        ),
    )
    def test_pages_availability_for_different_users(
            self, parametrized_client, expected_status, name, args
    ):
        url = reverse(name, args=args)
        response = parametrized_client.get(url)
        assert response.status_code == expected_status
