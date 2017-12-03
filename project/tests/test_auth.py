import json
import time
from flask import jsonify
from project import db
from project.utils import add_user
from project.api.models import User
from project.tests.base import BaseTestCase


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
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'test signed up.')
            self.assertTrue(data['data']['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_signup_empty_user(self):
        """ Verify empty user throws error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_signup_no_username(self):
        """ Verify signing up without a username throws an error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_signup_no_email(self):
        """ Verify signing up without an email throws an error. """
        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

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
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'error')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_signup_duplicate_username(self):
        """ Verify duplicate username throws error. """
        with self.client:
            self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/auth/signup',
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

    def test_signup_duplicate_email(self):
        """ Verify duplicate email throws error. """
        with self.client:
            self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test2',
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

    def test_signin_registered_user(self):
        """ Verify registered user can signin. """
        with self.client:
            self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'test signed in.')
            self.assertTrue(data['data']['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assert200(response)

    def test_not_registered_user_signin(self):
        """ Verify not registered user cannot signin. """
        with self.client:
            response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert404(response)

    def test_logout(self):
        """ Verify logout with valid token. """
        add_user('test', 'test@test.com', 'password')
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            logout_response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode()
                    )['data']['auth_token']
                }
            )
            data = json.loads(logout_response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'test logged out.')
            self.assert200(logout_response)

    def test_invalid_logout(self):
        """ Verify logout with invalid token. """
        with self.client:
            response = self.client.get(
                '/auth/logout',
                headers={ 'Authorization': 'Bearer invalid' }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Please signin again.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert401(response)

    def test_invalid_logout_expired_token(self):
        """ Verify logout with expired token. """
        add_user('test', 'test@test.com', 'password')
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            time.sleep(4)
            logout_response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode()
                    )['data']['auth_token']
                }
            )
            data = json.loads(logout_response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Signature expired. Please signin again.')
            self.assert401(logout_response)

    def test_invalid_logout_inactive(self):
        """ Verify inactive user logout throws error. """
        add_user('test', 'test@test.com', 'password')
        user = User.query.filter_by(email='test@test.com').first()
        user.active = False
        db.session.commit()
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            logout_response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode()
                    )['data']['auth_token']
                }
            )
            data = json.loads(logout_response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Something went wrong. Please contact us.')
            self.assert401(logout_response)

    def test_user_status(self):
        """ Verify GET request to /auth/status with valid token retrieves status. """
        add_user('test', 'test@test.com', 'password')
        with self.client:
            signin_response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'username': 'test',
                    'password': 'password'
                }),
                content_type='application/json'
            )
            status_response = self.client.get(
                '/auth/status',
                headers={
                    'Authorization': 'Bearer ' + json.loads(
                        signin_response.data.decode()
                    )['data']['auth_token']
                }
            )
            data = json.loads(status_response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['username'], 'test')
            self.assertEqual(data['data']['email'], 'test@test.com')
            self.assertTrue(data['data']['active'])
            self.assertTrue(data['data']['created_at'])
            self.assert200(status_response)

    def test_invalid_status(self):
        """ Verify GET request to /auth/status with invalid token throws error. """
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Please signin again.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert401(response)

