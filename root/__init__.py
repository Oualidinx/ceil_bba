
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from config import config
app = Flask(__name__)

database = SQLAlchemy()

login = LoginManager(app)

mail = Mail()

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
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_SERVER'] = "smtp.gmail.com"
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')


    mail.init_app(app)
    return app
