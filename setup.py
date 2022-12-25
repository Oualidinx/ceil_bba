from root import database, create_app
from root.models import User, Category, Level, Language
app = create_app('dev')
with app.app_context():
    user = User()
    user.role = "master"
    user.email= "admin@admin.com"
    from werkzeug.security import generate_password_hash
    import secrets
    password = secrets.token_hex(8)
    user.password_hash=generate_password_hash(password,"sha256")
    print(f"Utilisateur a été créer le mot de passe est {password}")
    database.session.add(user)
    database.session.commit()
    category = Category()
    category.label='Etudiant'
    category.price = 2000.00
    category.price_letters="Deux-mille dinars Algériens"
    database.session.add(category)
    database.session.commit()
    category = Category()
    category.label='Employé, université Mohamed El Bachir El Ibrahimi'
    category.price = 6000.00
    category.price_letters="Six-mille dinars Algériens"
    database.session.add(category)
    database.session.commit()
    category = Category()
    category.label='Externe'
    category.price = 8000.00
    category.price_letters="Huit-mille dinars Algériens"
    database.session.add(category)
    database.session.commit()
    level = Level()
    level.label = "A1"
    database.session.add(level)
    database.session.commit()
    level = Level()
    level.label = "A2"
    database.session.add(level)
    database.session.commit()
    level = Level()
    level.label = "B1"
    database.session.add(level)
    database.session.commit()
    level = Level()
    level.label = "B2"
    database.session.add(level)
    database.session.commit()
    level = Level()
    level.label = "C2"
    database.session.add(level)
    database.session.commit()
    level = Level()
    level.label = "C1"
    database.session.add(level)
    database.session.commit()


    langue = Language(label="Français")
    database.session.add(langue)
    database.session.commit()

    langue = Language(label="Anglais")
    database.session.add(langue)
    database.session.commit()


    langue = Language(label="Espagnole")
    database.session.add(langue)
    database.session.commit()