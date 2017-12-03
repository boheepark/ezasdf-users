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
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Users retrieved.')
            self.assertEqual(len(data['data']['users']), 2)
            self.assertEqual(data['data']['users'][1]['username'], 'test')
            self.assertEqual(data['data']['users'][1]['email'], 'test@test.com')
            self.assertEqual(data['data']['users'][0]['username'], 'test2')
            self.assertEqual(data['data']['users'][0]['email'], 'test2@test.com')
            self.assertIn('created_at', data['data']['users'][0])
            self.assertIn('created_at', data['data']['users'][1])
            self.assertEqual(response.content_type, 'application/json')

            self.assert200(response)

    def test_post_users(self):
        """ Verify POST request to /users adds a new user to the database. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'test@test.com was added!')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_post_users_empty(self):
        """ Verify adding an empty user throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_no_username(self):
        """ Verify adding a user without a username throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'password'
                }), content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_no_email(self):
        """ Verify adding a user without an email throws an error. """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_no_password(self):
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
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_duplicate(self):
        """ Verify adding a duplicate user throws an error. """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_duplicate_username(self):
        """ Verify adding a user with a duplicate username throws an error. """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test2@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_duplicate_email(self):
        """ Verify adding a user with a duplicate email throws an error. """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test2',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_get_users_by_id(self):
        """ Verify GET request to /users/{user_id} returns a user. """
        new_user = add_user('test', 'test@test.com', 'password')
        with self.client:
            response = self.client.get(f'/users/{new_user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], f'User {new_user.id} retrieved.')
            self.assertEqual(data['data']['username'], 'test')
            self.assertEqual(data['data']['email'], 'test@test.com')
            self.assertIn('created_at', data['data'])
            self.assertEqual(response.content_type, 'application/json')
            self.assert200(response)

    def test_get_users_invalid_id(self):
        """ Verify not existing id throws an error. """
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert404(response)

    def test_get_users_invalid_id_value(self):
        """ Verify requesting id 'blah' throws an error. """
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert404(response)

