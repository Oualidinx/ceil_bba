
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask
from flask_login import LoginManager
from flask_redmail import RedMail
from config import config
app = Flask(__name__)

database = SQLAlchemy()

login = LoginManager(app)

mail = RedMail()

def create_app(config_name):
    app.config.from_object(config[config_name])

    login.login_view = 'auth_bp.login'
    login.login_message_category = "info"
    from root.user import user_bp
    app.register_blueprint(user_bp)

    from root.authentication import auth_bp
    app.register_blueprint(auth_bp)

    from root.admin import admin_bp
    app.register_blueprint(admin_bp)

    database.init_app(app)
    app.config['EMAIL_PORT'] = 0
    app.config['EMAIL_HOST'] = "smtp.gmail.com"
    app.config['EMAIL_SENDER'] = "no-reply@ceil-bba.com"
    app.config['EMAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')


    mail.init_app(app)
    return app
