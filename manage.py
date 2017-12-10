# asdf-users/manage.py

import unittest
import coverage

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from project import create_app, db
from project.api.models import User

COV = coverage.coverage(branch=True, include='project/*', omit=['project/tests/*'])
COV.start()

app = create_app()

manager = Manager(app)
migrate = Migrate(app, db)


manager.add_command('db', MigrateCommand)


@manager.command
def cov():
    """ Runs the unit tests with coverage. """

    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


@manager.command
def test():
    """ Runs the unit tests without coverage. """

    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def seed_db():
    """ Seeds the database with sample data. """

    db.session.add(User(username='test', email='test@email.com', password='password'))
    db.session.add(User(username='test2', email='test2@email.com', password='password'))
    db.session.commit()


@manager.command
def recreate_db():
    """ Recreates the database. """

    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    manager.run()