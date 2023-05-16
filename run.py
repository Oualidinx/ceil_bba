from root import create_app, database as db
from flask import redirect, url_for
from root.models import User, Category, Level, Language
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
load_dotenv('.env')
application = create_app("prod")
with application.app_context():
    db.create_all()
    user = User()
    user.role = "master"
    user.email= os.environ.get('MAIL_USERNAME')+'@'+'univ-bba.dz'
    password = os.environ.get('PASSWORD')
    user.password_hash=generate_password_hash(password,"sha256")
    user.is_verified=1
    user.is_deleted=0

    db.session.add(user)
    db.session.commit()

    category = Category()
    category.label='Etudiant'
    category.price = 2000.00
    category.price_letters="Deux-mille dinars Algériens"
    db.session.add(category)
    db.session.commit()

    category = Category()
    category.label='Employé, université Mohamed El Bachir El Ibrahimi'
    category.price = 1000.00
    category.price_letters="Six-mille dinars Algériens"
    db.session.add(category)
    db.session.commit()

    category = Category()
    category.label='Externe'
    category.price = 8000.00
    category.price_letters="Huit-mille dinars Algériens"
    db.session.add(category)
    db.session.commit()

    level = Level()
    level.label = "A1"
    db.session.add(level)
    db.session.commit()

    level = Level()
    level.label = "A2"
    db.session.add(level)
    db.session.commit()

    level = Level()
    level.label = "B1"
    db.session.add(level)
    db.session.commit()

    level = Level()
    level.label = "B2"
    db.session.add(level)
    db.session.commit()

    level = Level()
    level.label = "C2"
    db.session.add(level)
    db.session.commit()

    level = Level()
    level.label = "C1"
    db.session.add(level)
    db.session.commit()

    langue = Language(label="Anglais")
    db.session.add(langue)
    db.session.commit()

@application.route('/')
def index():
    return redirect(url_for('auth_bp.register'))
if __name__=="__main__":
    application.run(debug=False)