from flask_migrate import Migrate
from root import create_app,database
from flask import redirect, url_for
import os
from root.models import *
from dotenv import load_dotenv

load_dotenv('.env')
app = create_app(os.environ.get('FLASK_ENV'))
app.config.update(dict(
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ))
migrate = Migrate(app=app, db=database)

@app.route('/')
def index():
    return redirect(url_for('auth_bp.login'))

@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=database,
                User=User
                )
