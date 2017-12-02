import os
import unittest
from flask import current_app
from flask_testing import TestCase

from project import create_app


app = create_app()


class TestDevelopmentConfig(TestCase):
    """ Tests for Development Configuration. """

    def create_app(self):
        """ Setup Development Configurations.
        :return: flask app
        """
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        """ Verify app is configured for development. """
        self.assertEqual(app.config['SECRET_KEY'], os.getenv('SECRET_KEY'))
        self.assertTrue(app.config['DEBUG'])
        self.assertIsNotNone(current_app)
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], os.getenv('DATABASE_URL'))
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(app.config['TOKEN_EXPIRATION_DAYS'], 30)
        self.assertEqual(app.config['TOKEN_EXPIRATION_SECONDS'], 0)


class TestTestingConfig(TestCase):
    """ Tests for Testing Configuration. """

    def create_app(self):
        """ Setup Testing Configurations
        :return: flask app
        """
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        """ Verify app is configured for testing. """
        self.assertEqual(app.config['SECRET_KEY'], os.getenv('SECRET_KEY'))
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], os.getenv('DATABASE_TEST_URL'))
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(app.config['TOKEN_EXPIRATION_DAYS'], 0)
        self.assertEqual(app.config['TOKEN_EXPIRATION_SECONDS'], 3)


class TestProductionConfig(TestCase):
    """ Tests for Production Configuration. """

    def create_app(self):
        """ Setup Production Configurations.
        :return: flask app
        """
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        """ Verify app is configured for production. """
        self.assertEqual(app.config['SECRET_KEY'], os.getenv('SECRET_KEY'))
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 13)
        self.assertEqual(app.config['TOKEN_EXPIRATION_DAYS'], 30)
        self.assertEqual(app.config['TOKEN_EXPIRATION_SECONDS'], 0)


if __name__ == '__main__':
    unittest.main()