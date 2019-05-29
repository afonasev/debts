from http import HTTPStatus
from unittest.mock import ANY

import pytest

from server.config import config
from server.db import Person

COOKIES = {config.ACCESS_TOKEN_COOKIE: ''}


@pytest.fixture(autouse=True)
def _mock_check_token(mocker, user):
    mocker.patch('jwt.decode', return_value={'id': user.id})


def test_get_persons(client, person):
    response = client.get(
        f'/api/users/{person.user_id}/persons', cookies=COOKIES
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'balance': person.balance,
            'id': person.id,
            'name': person.name,
            'user_id': person.user_id,
            'created': ANY,
        }
    ]


def test_create_person(client, user, db_session):
    response = client.post(
        f'/api/users/{user.id}/persons', cookies=COOKIES, json={'name': 'name'}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': ANY,
        'balance': 0,
        'name': 'name',
        'user_id': user.id,
        'created': ANY,
    }

    assert db_session.query(Person).filter_by(id=response.json()['id']).one()


def test_create_person_duplicate_name(client, person):
    response = client.post(
        f'/api/users/{person.user_id}/persons',
        cookies=COOKIES,
        json={'name': person.name},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_person(client, person, db_session):
    response = client.delete(
        f'/api/users/{person.user_id}/persons/{person.id}', cookies=COOKIES
    )
    assert response.status_code == HTTPStatus.OK
    assert db_session.query(Person).filter_by(id=person.id).one().deleted


def test_delete_person_not_founed(client, person, db_session):
    response = client.delete(
        f'/api/users/{person.user_id}/persons/0', cookies=COOKIES
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
