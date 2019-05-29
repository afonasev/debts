from http import HTTPStatus
from unittest.mock import ANY

from server.db import User

TEST_EMAIL = 'name@domain.com'
TEST_PASSWORD = 'password'
USER_JSON = {'email': TEST_EMAIL, 'password': TEST_PASSWORD}


def test_create_user(client, db_session):
    response = client.post('/api/auth/users', json=USER_JSON)

    assert response.status_code == HTTPStatus.CREATED

    db_user = db_session.query(User).filter_by(email=TEST_EMAIL).one()
    assert response.json() == {
        'id': db_user.id,
        'email': db_user.email,
        'token': ANY,
    }


def test_create_duplicate_user(client, user, db_session):
    response = client.post(
        '/api/auth/users',
        json={'email': user.email, 'password': TEST_PASSWORD},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_token(client, db_session):
    client.post('/api/auth/users', json=USER_JSON)
    response = client.post('/api/auth/token', json=USER_JSON)

    assert response.status_code == HTTPStatus.OK

    db_user = db_session.query(User).filter_by(email=TEST_EMAIL).one()
    assert response.json() == {
        'id': db_user.id,
        'email': db_user.email,
        'token': ANY,
    }


def test_create_token_user_not_exists(client, user):
    response = client.post('/api/auth/token', json=USER_JSON)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_token_wrong_password(client, user):
    client.post('/api/auth/users', json=USER_JSON)
    response = client.post(
        '/api/auth/token', json={'email': TEST_EMAIL, 'password': 'wrong'}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_request_without_token(client, person):
    response = client.get(f'/api/users/{person.user_id}/persons')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_with_wrong_token(client, person, access_token):
    response = client.get(
        '/api/users/0/persons',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_with_broken_token(client, person):
    response = client.get(
        f'/api/users/{person.user_id}/persons',
        headers={'Authorization': f'Bearer wrong_token'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_request_with_token(client, person, access_token):
    response = client.get(
        f'/api/users/{person.user_id}/persons',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
