# ezasdf-users/project/tests/test_auth.py


import json
import time

from project import db
from project.api.utils import add_user, get_jwt
from project.tests.base import BaseTestCase
from project.tests.utils import (
    USERNAME,
    USERNAME2,
    EMAIL,
    EMAIL2,
    PASSWORD
)


class TestAuthBlueprint(BaseTestCase):
    """ Tests for the auth blueprint. """

    def test_post_signup(self):
        """ Verify a new user can sign up. """

        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], f'{EMAIL} signed up.')
            self.assertTrue(data['data']['token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_post_signup_empty_user(self):
        """ Verify an empty user cannot sign up. """

        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_signup_no_username(self):
        """ Verify a username is required for signing up. """

        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_signup_no_email(self):
        """ Verify an email is required for signing up. """

        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'password': PASSWORD
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_signup_no_password(self):
        """ Verify a password is required for signing up. """

        with self.client:
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_signup_duplicate_username(self):
        """ Verify users cannot signup with duplicate username. """

        with self.client:
            self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL2,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_signup_duplicate_email(self):
        """ Verify users cannot signup with a duplicate email. """

        with self.client:
            self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME2,
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User already exists.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert400(response)

    def test_post_signin_registered_user(self):
        """ Verify registered users can signin. """

        with self.client:
            self.client.post(
                '/auth/signup',
                data=json.dumps({
                    'username': USERNAME,
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], f'{EMAIL} signed in.')
            self.assertTrue(data['data']['token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assert200(response)

    def test_post_signin_not_registered_user(self):
        """ Verify not registered users cannot get_jwt. """

        with self.client:
            response = self.client.post(
                '/auth/signin',
                data=json.dumps({
                    'email': EMAIL,
                    'password': PASSWORD
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert404(response)

    def test_get_signout(self):
        """ Verify users can sign out. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            token = get_jwt(self.client, user.email)
            response = self.client.get(
                '/auth/signout',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], f'{user.email} signed out.')
            self.assert200(response)

    def test_get_signout_invalid_user(self):
        """ Verify signing out a user with an invalid token throws an error. """

        with self.client:
            response = self.client.get(
                '/auth/signout',
                headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Signin again.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert401(response)

    def test_get_signout_user_with_expired_token(self):
        """ Verify signing out a user with an expired token throws an error. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            token = get_jwt(self.client, user.email)
            time.sleep(4)
            response = self.client.get(
                '/auth/signout',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Signature expired. Signin again.')
            self.assert401(response)

    def test_get_signout_inactive_user(self):
        """ Verify signing out an inactive user throws an error. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        user.active = False
        db.session.commit()
        with self.client:
            token = get_jwt(self.client, user.email)
            response = self.client.get(
                '/auth/signout',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Something went wrong. Please contact us.')
            self.assert401(response)

    def test_get_profile(self):
        """ Verify user can get profile with valid token. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        with self.client:
            token = get_jwt(self.client, user.email)
            response = self.client.get(
                '/auth/profile',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], f"Fetched {user.email}'s profile data.")
            self.assertEqual(data['data']['username'], user.username)
            self.assertEqual(data['data']['email'], user.email)
            self.assertTrue(data['data']['active'])
            self.assertTrue(data['data']['created_at'])
            self.assert200(response)

    def test_get_profile_invalid_token(self):
        """ Verify user cannot get profile with invalid token. """

        with self.client:
            response = self.client.get(
                '/auth/profile',
                headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Signin again.')
            self.assertEqual(response.content_type, 'application/json')
            self.assert401(response)

    def test_get_profile_inactive_user(self):
        """ Verify getting the profile of an inactive user throws an error. """

        user = add_user(USERNAME, EMAIL, PASSWORD)
        user.active = False
        db.session.commit()
        with self.client:
            token = get_jwt(self.client, user.email)
            response = self.client.get(
                '/auth/profile',
                headers={'Authorization': 'Bearer ' + token}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Something went wrong. Please contact us.')
            self.assert401(response)
