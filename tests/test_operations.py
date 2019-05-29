from http import HTTPStatus
from unittest.mock import ANY

from server.db import Operation, Person


def test_get_operations(client, person, operation, headers):
    response = client.get(
        f'/api/users/{person.user_id}/persons/{person.id}/operations',
        headers=headers,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': operation.id,
            'person_id': person.id,
            'value': float(operation.value),
            'description': operation.description,
            'created': ANY,
        }
    ]


def test_get_operations_with_wrong_person(client, person, headers):
    response = client.get(
        f'/api/users/{person.user_id}/persons/0/operations', headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_operation(client, person, db_session, headers):
    operation_data = {'value': 10, 'description': 'description'}

    response = client.post(
        f'/api/users/{person.user_id}/persons/{person.id}/operations',
        headers=headers,
        json=operation_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': ANY,
        'person_id': person.id,
        'value': operation_data['value'],
        'description': operation_data['description'],
        'created': ANY,
    }

    operation_id = response.json()['id']
    assert db_session.query(Operation).filter_by(id=operation_id).one()

    update_person = db_session.query(Person).filter_by(id=person.id).one()
    assert update_person.balance == person.balance + operation_data['value']


def test_delete_operation(client, person, operation, db_session, headers):
    response = client.delete(
        f'/api/users/{person.user_id}/persons/{person.id}/operations/{operation.id}',
        headers=headers,
    )
    assert response.status_code == HTTPStatus.OK
    assert db_session.query(Operation).filter_by(id=operation.id).one().deleted

    update_person = db_session.query(Person).filter_by(id=person.id).one()
    assert update_person.balance == person.balance - operation.value


def test_delete_person_not_founed(client, person, db_session, headers):
    response = client.delete(
        f'/api/users/{person.user_id}/persons/{person.id}/operations/0',
        headers=headers,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
