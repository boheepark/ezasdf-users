# ezasdf-users/ezasdf_users.py


import unittest

import coverage
import click

from flask_migrate import Migrate

from project import create_app, db
from project.api.models import User


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*'
    ]
)
COV.start()


app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {
        'app': app,
        'db': db,
        'User': User
    }


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Enable code coverage')
def test(coverage):
    """ Run the unit tests. """

    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        if cov:
            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()
            COV.html_report()
            COV.erase()
        return 0
    return 1


@app.cli.command()
def recreate_db():
    """ Recreates the database. """

    db.drop_all()
    db.create_all()
    db.session.commit()


@app.cli.command()
def seed_db():
    """ Seeds the database with sample data. """

    db.session.add(User(username='test', email='test@email.com', password='password'))
    db.session.add(User(username='test2', email='test2@email.com', password='password'))
    db.session.commit()
