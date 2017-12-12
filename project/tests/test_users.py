# ezasdf-users/project/tests/test_users.py


import datetime
import json

from project import db
from project.tests.base import BaseTestCase
from project.api.utils import (
    add_user,
    add_admin,
    get_jwt
)
from project.tests.utils import (
    USERNAME,
    USERNAME2,
    EMAIL,
    EMAIL2,
    PASSWORD
)


class TestUsersBlueprint(BaseTestCase):
    """ Tests for the users blueprint. """

    def test_get_users_ping(self):
        """ Sanity check. """

        with self.client:
            response = self.client.get('/users/ping')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'pong!')
            self.assert200(response)

    def test_get_users(self):
        """ Verify GET request to /users returns a list of users ordered by created_at. """

        created = datetime.datetime.utcnow() + datetime.timedelta(-30)
        user = add_user(USERNAME, EMAIL, PASSWORD, created)
        user2 = add_user(USERNAME2, EMAIL2, PASSWORD)
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Users fetched.')
            self.assertEqual(len(data['data']['users']), 2)
            self.assertEqual(data['data']['users'][1]['username'], user.username)
            self.assertEqual(data['data']['users'][1]['email'], user.email)
            self.assertEqual(data['data']['users'][0]['username'], user2.username)
            self.assertEqual(data['data']['users'][0]['email'], user2.email)
            self.assertIn('created_at', data['data']['users'][0])
            self.assertIn('created_at', data['data']['users'][1])
            self.assertEqual(response.content_type, 'application/json')
            self.assert200(response)

    def test_post_users_with_not_admin_user_token(self):
        """ Verify non admins cannot add a new user. """

        user = add_user(USERNAME, EMAIL, 'password')
        with self.client:
            token = get_jwt(self.client, user.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test2',
                    'email': EMAIL2,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'You do not have permission to do that.')
            self.assert401(response)

    def test_post_users(self):
        """ Verify POST request to /users adds a new user to the database. """

        admin = add_admin()
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], '{email} was added!'.format(email=EMAIL))
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_post_users_empty(self):
        """ Verify adding an empty user throws an error. """

        admin = add_admin()
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_no_username(self):
        """ Verify adding a user without a username throws an error. """

        admin = add_admin()
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_no_email(self):
        """ Verify adding a user without an email throws an error. """

        admin = add_admin()
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': USERNAME,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_no_password(self):
        """ Verify adding a user without a password throws an error. """

        admin = add_admin()
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_duplicate_user(self):
        """ Verify adding a duplicate user throws an error. """

        admin = add_admin()
        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': user.username,
                    'email': user.email,
                    'password': user.password
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_duplicate_username(self):
        """ Verify adding a user with a duplicate username throws an error. """

        admin = add_admin()
        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': user.username,
                    'email': EMAIL2,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_duplicate_email(self):
        """ Verify adding a user with a duplicate email throws an error. """

        admin = add_admin()
        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            token = get_jwt(self.client, admin.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': USERNAME2,
                    'email': user.email,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_users_inactive_user(self):
        """ Verify adding an inactive user throws an error. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        user.active = False
        db.session.commit()
        with self.client:
            token = get_jwt(self.client, user.email)
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': USERNAME2,
                    'email': EMAIL2,
                    'password': PASSWORD
                }),
                content_type='application/json',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Something went wrong. Please contact us.')
            self.assert401(response)

    def test_get_users_by_id(self):
        """ Verify GET request to /users/{user_id} fetches a user. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            response = self.client.get('/users/{user_id}'.format(user_id=user.id))
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'User {user_id} fetched.'.format(user_id=user.id))
            self.assertEqual(data['data']['username'], 'test')
            self.assertEqual(data['data']['email'], 'test@email.com')
            self.assertIn('created_at', data['data'])
            self.assertEqual(response.content_type, 'application/json')
            self.assert200(response)

    def test_get_users_invalid_id(self):
        """ Verify fetching an id that doesn't exist throws an error. """

        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert404(response)

    def test_get_users_invalid_id_value(self):
        """ Verify requesting the invalid id 'blah' throws an error. """

        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert404(response)
