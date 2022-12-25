from flask_login import current_user
from flask_wtf import FlaskForm, Form
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from wtforms import SubmitField, StringField, PasswordField, TextAreaField, BooleanField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField, EmailField
from root.models import User, Language, Session, Course, Category, Level
from sqlalchemy.sql import and_

import re
email_regex = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
name_regex = re.compile('^[a-zA-z]+$')
phone_number_regex = re.compile('^[\+]?[(]?[0-9]{2}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,7}$')


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired()])
    password = PasswordField('Mot de passe: ', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

    def validate_email(self, email):
        if email_regex.search(email.data) is None:
            raise ValidationError('Email Invalid')
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Veuillez vérifier les informations fournits')


class UpdateInfoForm(FlaskForm):
    first_name = StringField('Nom: ')
    last_name = StringField('Prénom: ')
    birthday = DateField('Date de naissance: ')
    email = StringField('Email: ')
    password = PasswordField('Mot de passe:')
    confirm_password = PasswordField('Confirmer Mot de passe:', validators=[EqualTo('password',
                                                                            message="Vérifier bien ce champs S.V.P")])
    submit = SubmitField('Mise à jour')

    def validate_first_name(self, first_name):
        if name_regex.search(first_name.data) is None:
            raise ValidationError('Nom Invalide')

    def validate_last_name(self, last_name):
        if name_regex.search(last_name.data) is None:
            raise ValidationError('Prénom Invalide')

    def validate_email(self, email):
        if email_regex.search(email.data) is None:
            raise ValidationError('Email Invalid')
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user:
    #         raise ValidationError('Cet email est déjà utilisé')

class RegistrationForm(FlaskForm):
    first_name = StringField('Nom: ', validators=[DataRequired()])
    last_name = StringField('Prénom: ', validators=[DataRequired()])
    birthday = DateField('Date de naissance: ')
    email = StringField('Email: ', validators=[DataRequired()])
    password = PasswordField('Mot de passe:', validators=[DataRequired()])
    category = QuerySelectField('Catégorie', query_factory=lambda : Category.query.all())
    confirm_password = PasswordField('Confirmer Mot de passe:', validators=[DataRequired(),
                                                                            EqualTo('password',
                                                                            message="Vérifier bien ce champs S.V.P")])
    submit = SubmitField('Inscrire')

    def validate_first_name(self, first_name):
        if name_regex.search(first_name.data) is None:
            raise ValidationError('Nom Invalide')

    def validate_last_name(self, last_name):
        if name_regex.search(last_name.data) is None:
            raise ValidationError('Prénom Invalide')

    def validate_email(self, email):
        if email_regex.search(email.data) is None:
            raise ValidationError('Email Invalid')
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé')


class AddCourseForm(FlaskForm):
    label = StringField('Libellé: ', validators=[DataRequired(message="Champs obligatoire")])
    price = StringField('Prix:')# validators=[DataRequired(message="Champs obligatoire")]
    session = QuerySelectField('Session: ', query_factory=lambda : Session.query.filter_by(is_active = True).filter_by(is_disabled = False).all())
    language = QuerySelectField('Langue: ', query_factory=lambda : Language.query.all())
    level = QuerySelectField('Niveau: ', query_factory=lambda : Level.query.all())
    limit_number = StringField('Nombre Maximum des inscrits:', validators=[DataRequired('Ce champs est obligatoire')])
    on_test = BooleanField('Teste de niveau: ')
    description = TextAreaField('Description sur la formation: ', validators=[Length(max=2500)])
    submit = SubmitField('Confirmer')

    def validate_limit_number(self, limit_number):
        if int(limit_number.data) < 0:
            raise ValidationError('Ce nombre doit être supérieur à 0')


class CoursesForm(Form):
    label = StringField('Titre: ', validators=[DataRequired(message="Champs obligatoire")])
    price = StringField('Prix: ', validators=[DataRequired(message='Champs obligatoire')])
    description = StringField('Description sur la formation: ')
    delete_entry=SubmitField('Supprimer')


class SubscriptionForm(FlaskForm):
    # courses = FieldList(FormField(CoursesForm), validators=[DataRequired()])
    course = QuerySelectField('Formation:', query_factory=lambda: Course.query.filter_by(is_disabled = False).all())
    # add = SubmitField('Ajouter Formation')
    submit = SubmitField('Confirmer le choix')


class SessionForm(FlaskForm):
    label = StringField('Libellé: ')
    start_date = DateField('Date début: ', validators=[DataRequired()])
    end_date = DateField('Date fin: ', validators=[DataRequired()])
    # courses = FieldList(FormField(CoursesForm), validators=[DataRequired()])
    add_language = SubmitField('Ajouter Formation')
    submit = SubmitField('Ajouter')

    def validate_label(self, label):
        user = Session.query.filter_by(label=label.data).filter_by(is_active = True).first()
        if user:
            raise ValidationError('libellé déjà utilisé')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Nouveau mot de passe:', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mot de passe:', validators=[DataRequired(), EqualTo('new_password', "Vérifier le mot de passe")])
    submit = SubmitField('MAJ')


class RequestToken(FlaskForm):
    email = EmailField('Saisissez votre email: ', validators=[DataRequired()])
    submit = SubmitField('Envoyer')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).filter_by(role="student").filter_by(is_deleted = 0).first()
        if not user:
            raise ValidationError('Email invalide')


class CategoryForm(FlaskForm):
    label = StringField('Libellé: ', validators=[DataRequired()])
    price = StringField("Prix par la catégorie: ", validators=[DataRequired("Champs obligatoire")])
    submit = SubmitField('Confirmer')

    def validate_label(self, label):
        category = Category.query.filter_by(label = label.data).first()
        if category:
            raise ValidationError('Catégorie existe déjà')


class EnableSubscription(FlaskForm):
    enable = RadioField('Ouvrir/fermer les inscriptions: ', choices=[('o', 'Ouvrir'),('f','Fermer')])
    submit = SubmitField('Confirmer les info.')


class EditCategoryForm(FlaskForm):
    id = StringField()
    label = StringField('Titre de catégorie: ')
    price = StringField("Prix par la catégorie: ", validators=[DataRequired("Champs obligatoire")])
    submit = SubmitField('Mettre à jour')
    def validate_price(self, price):
        if float(price.data) < 0:
            raise ValidationError('Valeur ne doit pas inférieur de 0')


class EditCourseForm(AddCourseForm):
    submit = SubmitField('Confirmer')