import json
from project import db
from project.api.models import User
from project.tests.base import BaseTestCase

def add_user(username, email):
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return new_user

class TestUserService(BaseTestCase):

    def test_add_user(self):
        with self.client:
            res = self.client.post('/users', data=json.dumps({
                "username": "test",
                "email": "test@test.com"
            }), content_type='application/json')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 201)
            self.assertIn('test@test.com was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_empty_user(self):
        with self.client:
            res = self.client.post('/users', data=json.dumps({}), content_type='application/json')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_with_no_username(self):
        with self.client:
            res = self.client.post('/users', data=json.dumps({'email': 'test@test.com'}), content_type='application/json')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_duplicate_user(self):
        with self.client:
            self.client.post('/users', data=json.dumps({
                "username": "test",
                "email": "test@test.com"
            }), content_type='application/json')
            res = self.client.post('/users', data=json.dumps({
                "username": "test",
                "email": "test@test.com"
            }), content_type='application/json')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertIn('Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_user(self):
        new_user = add_user('test', 'test@test.com')
        with self.client:
            res = self.client.get(f'/users/{new_user.id}')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertIn('created_at', data['data'])
            self.assertIn('test', data['data']['username'])
            self.assertIn('test@test.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_get_user_bad_id(self):
        with self.client:
            res = self.client.get('/users/blah')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_users(self):
        add_user('test', 'test@test.com')
        add_user('test2', 'test2@test.com')
        with self.client:
            res = self.client.get('/users')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('created_at', data['data']['users'][0])
            self.assertIn('created_at', data['data']['users'][1])
            self.assertIn('test', data['data']['users'][0]['username'])
            self.assertIn('test@test.com', data['data']['users'][0]['email'])
            self.assertIn('test2', data['data']['users'][1]['username'])
            self.assertIn('test2@test.com', data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])