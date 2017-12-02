import json
import time
from project.tests.base import BaseTestCase
from project.utils import add_user


class TestAuthBlueprint(BaseTestCase):
    """ Tests for the auth blueprint. """

    def test_signup(self):
        """ Verify POST request to /auth/signup registers a new user. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_signup_empty_user(self):
        """ Verify empty user throws error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({}),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertEqual('error', data['status'])

    def test_signup_no_username(self):
        """ Verify signing up without a username throws an error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertEqual('error', data['status'])

    def test_signup_no_password(self):
        """ Verify signing up without a password throws an error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertEqual('error', data['status'])

    def test_signup_no_email(self):
        """ Verify signing up without an email throws an error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json',
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertEqual('error', data['status'])

    def test_signup_duplicate_email(self):
        """ Verify duplicate email throws error. """
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username':'test2',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('That user already exists.', data['message'])
            self.assertEqual('error', data['status'])

    def test_signup_duplicate_username(self):
        """ Verify duplicate username throws error. """
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test2@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert400(response)
            data = json.loads(response.data.decode())
            self.assertEqual('That user already exists.', data['message'])
            self.assertEqual('error', data['status'])

    def test_registered_user_signin(self):
        """ Verify registered user can signin. """
        with self.client:
            add_user('test', 'test@test.com', 'test')
            response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert200(response)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully signed in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')

    def test_not_registered_user_signin(self):
        """ Verify not registered user cannot signin. """
        with self.client:
            response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            self.assert404(response)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')

    def test_valid_logout(self):
        """ Verify logout with valid token. """
        add_user('test', 'test@test.com', 'test')
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            logout_response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode())['auth_token']
                }
            )
            self.assert200(logout_response)
            data = json.loads(logout_response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully logged out.')

    def test_invalid_logout(self):
        """ Verify logout with invalid token. """
        with self.client:
            response = self.client.get(
                '/auth/logout',
                headers={ 'Authorization': 'Bearer invalid' }
            )
            self.assert401(response)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Please signin again.')

    def test_invalid_logout_expired_token(self):
        """ Verify logout with expired token. """
        add_user('test', 'test@test.com', 'test')
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            time.sleep(4)
            logout_response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode())['auth_token']
                }
            )
            self.assert401(logout_response)
            data = json.loads(logout_response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Signature expired. Please signin again.')

    def test_user_status(self):
        """ Verify GET request to /auth/status with valid token retrieves status. """
        add_user('test', 'test@test.com', 'test')
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            status_response = self.client.get(
                '/auth/status',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode()
                    )['auth_token']
                }
            )
            self.assert200(status_response)
            data = json.loads(status_response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data['data'])
            self.assertEqual(data['data']['username'], 'test')
            self.assertEqual(data['data']['email'], 'test@test.com')
            self.assertTrue(data['data']['active'])
            self.assertTrue(data['data']['created_at'])

    def test_invalid_status(self):
        """ Verify GET request to /auth/status with invalid token throws error. """
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={ 'Authorization': 'Bearer invalid' }
            )
            self.assert401(response)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Please signin again.')
