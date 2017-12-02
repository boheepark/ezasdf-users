import datetime
import json
from project.tests.base import BaseTestCase
from project.utils import add_user


class TestUsersBlueprint(BaseTestCase):
    """ Tests for the users blueprint. """

    def test_get_users(self):
        """ Verify GET request to /users returns a list of users ordered by created_at. """
        created = datetime.datetime.utcnow() + datetime.timedelta(-30)
        add_user('test', 'test@test.com', 'test', created)
        add_user('test2', 'test2@test.com', 'test')
        with self.client:
            response = self.client.get('/users')
            self.assert200(response)
            data = json.loads(response.data.decode())
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('created_at', data['data']['users'][0])
            self.assertIn('created_at', data['data']['users'][1])
            self.assertEqual('test', data['data']['users'][1]['username'])
            self.assertEqual('test@test.com', data['data']['users'][1]['email'])
            self.assertEqual('test2', data['data']['users'][0]['username'])
            self.assertEqual('test2@test.com', data['data']['users'][0]['email'])
            self.assertEqual('success', data['status'])

    def test_add_user(self):
        """ Verify POST request to /users adds a new user to the database. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data.decode())
            self.assertEqual('test@test.com was added!', data['message'])
            self.assertEqual('success', data['status'])

    def test_add_empty_user(self):
        """ Verify adding an empty user throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_no_username(self):
        """ Verify adding a user without a username throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }), content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_no_email(self):
        """ Verify adding a user without an email throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_no_password(self):
        """ Verify adding a user without a password throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_duplicate_user(self):
        """ Verify adding a duplicate user throws an error. """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertIn('That user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_duplicate_username(self):
        """ Verify adding a user with a duplicate username throws an error. """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test2@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertIn('That user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_duplicate_email(self):
        """ Verify adding a user with a duplicate email throws an error. """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test2',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertIn('That user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_user_invalid_id(self):
        """ Verify requesting id 'blah' throws an error. """
        with self.client:
            response = self.client.get('/users/blah')
            self.assert404(response)
            data = json.loads(response.data.decode())
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_user_by_id(self):
        """ Verify GET request to /users/{user_id} returns a user. """
        new_user = add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.get(f'/users/{new_user.id}')
            self.assert200(response)
            data = json.loads(response.data.decode())
            self.assertIn('created_at', data['data'])
            self.assertIn('test', data['data']['username'])
            self.assertIn('test@test.com', data['data']['email'])
            self.assertIn('success', data['status'])