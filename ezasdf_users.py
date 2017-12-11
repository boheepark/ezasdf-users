# ezasdf-users/ezasdf_users.py


from flask_migrate import Migrate

from project import create_app, db
from project.api.models import User


app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {
        'app': app,
        'db': db,
        'User': User
    }