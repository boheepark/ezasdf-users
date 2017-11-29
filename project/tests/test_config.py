import unittest
from flask import current_app
from flask_testing import TestCase

from project import create_app

app = create_app()

class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertEqual(app.config['SECRET_KEY'], 'asdf')
        self.assertTrue(app.config['DEBUG'])
        self.assertIsNotNone(current_app)
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'postgres://postgres:postgres@users-db:5432/users_dev')


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertEqual(app.config['SECRET_KEY'], 'asdf')
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'postgres://postgres:postgres@users-db:5432/users_test')


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertEqual(app.config['SECRET_KEY'], 'asdf')
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])


if __name__ == '__main__':
    unittest.main()