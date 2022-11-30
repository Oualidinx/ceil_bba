from flask_migrate import Migrate
from root import create_app
from root import database as db

import os
from root.models import User
from dotenv import load_dotenv

load_dotenv('.env')
app = create_app(os.environ.get('FLASK_ENV'))
app.config.update(dict(
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ))
migrate = Migrate(app=app, db=db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=db,
                User=User
                )
