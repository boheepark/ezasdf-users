import datetime
from project import db
from project.api.models import User


def add_user(username, email, password, created_at=datetime.datetime.utcnow()):
    """ Helper function for adding a new user to the database.
    :param username:
    :param email:
    :param password:
    :param created_at:
    :return: User object
    """
    new_user = User(
        username=username,
        email=email,
        password=password,
        created_at=created_at
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user
