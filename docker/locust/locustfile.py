import logging
import random
import uuid
from typing import Dict, List

from locust import HttpLocust, TaskSequence, task

logger = logging.getLogger('locust')


class NormalUser(TaskSequence):
    id: str
    email: str
    token: str
    persons: List[str]

    def on_start(self) -> None:
        self.email = f'{uuid.uuid4()}@m.com'
        response = self.client.post(
            '/auth/users', json={'email': self.email, 'password': 'pass'}
        )
        response.raise_for_status()
        self.id = response.json()['id']
        self.token = response.json()['token']
        self.persons = []

    @task(4)
    def create_person(self) -> None:
        response = self.client.post(
            f'/users/{self.id}/persons',
            name='/users/{user_id}/persons',
            json={'name': uuid.uuid4().hex},
            headers=self.headers,
        )
        response.raise_for_status()
        self.persons.append(response.json()['id'])

    @task(9)
    def get_persons(self) -> None:
        response = self.client.get(
            f'/users/{self.id}/persons',
            name='/users/{user_id}/persons',
            headers=self.headers
        )
        response.raise_for_status()

    @task(6)
    def create_operation(self) -> None:
        if not self.persons:
            return

        person_id = random.choice(self.persons)

        response = self.client.post(
            f'/users/{self.id}/persons/{person_id}/operations',
            name='/users/{user_id}/persons/{person_id}/operations',
            json={'value': random.randint(0, 100), 'description': 'description'},
            headers=self.headers,
        )
        response.raise_for_status()

    @task(11)
    def get_operations(self) -> None:
        if not self.persons:
            return

        person_id = random.choice(self.persons)

        response = self.client.get(
            f'/users/{self.id}/persons/{person_id}/operations',
            name='/users/{user_id}/persons/{person_id}/operations',
            headers=self.headers
        )
        response.raise_for_status()

    @task(1)
    def get_token(self) -> None:
        response = self.client.post(
            '/auth/token', json={'email': self.email, 'password': 'pass'}
        )
        response.raise_for_status()
        self.token = response.json()['token']

    @property
    def headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.token}'}


class NormalLocust(HttpLocust):
    task_set = NormalUser
    min_wait = 100
    max_wait = 1000
