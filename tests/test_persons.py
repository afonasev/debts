from http import HTTPStatus
from unittest.mock import ANY

from server.db import Person


def test_get_persons(client, person, headers):
    response = client.get(
        f'/api/users/{person.user_id}/persons', headers=headers
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


def test_create_person(client, user, db_session, headers):
    response = client.post(
        f'/api/users/{user.id}/persons', headers=headers, json={'name': 'name'}
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


def test_create_person_duplicate_name(client, person, headers):
    response = client.post(
        f'/api/users/{person.user_id}/persons',
        headers=headers,
        json={'name': person.name},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_person(client, person, db_session, headers):
    response = client.delete(
        f'/api/users/{person.user_id}/persons/{person.id}', headers=headers
    )
    assert response.status_code == HTTPStatus.OK
    assert db_session.query(Person).filter_by(id=person.id).one().deleted


def test_delete_person_not_founed(client, person, db_session, headers):
    response = client.delete(
        f'/api/users/{person.user_id}/persons/0', headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
