from root import database as db
from flask_login import UserMixin
from root import login
from flask import current_app
from datetime import datetime, timedelta
# from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import json
import jwt
from time import time
from root import app

class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return (str(z))
        else:
            return super().default(z)


class Course(db.Model):
    __tablename__="course"
    id = db.Column(db.Integer, primary_key = True)
    label = db.Column(db.String(100))
    price = db.Column(db.Float, default = 0)
    is_disabled = db.Column(db.Boolean, default = False)
    fk_session_id=db.Column(db.Integer, db.ForeignKey('session.id'))
    description = db.String(db.String(2500))
    on_test = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return dict(
            id = self.id,
            label = self.label,
            status = ('Désactivé','warning') if not self.is_disabled else ("Activé", 'success'),
            session=Session.query.get(self.fk_session_id).label
        )


class Category(db.Model):
    __tablename__="category"
    id = db.Column(db.Integer, primary_key = True)
    label = db.Column(db.String(100))
    students = db.relationship('User', backref="category_students", lazy="subquery")
    def __repr__(self):
        return f'{self.label}'


class Level(db.Model):
    __tablename__="level"
    id = db.Column(db.Integer, primary_key = True)
    label = db.Column(db.String(100))
    def __repr__(self):
        return f'{self.label}'



class User(UserMixin, db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    birthday = db.Column(db.Date)
    role = db.Column(db.String(10))
    fk_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    is_deleted = db.Column(db.SmallInteger, default=0)
    email = db.Column(db.String(100), nullable = False)
    phone_number = db.Column(db.String(10))
    password_hash = db.Column(db.String(256), nullable=False)
    courses = db.relationship('Course', secondary="subscription",
                                    backref="user_subscription",
                                    primaryjoin="User.id==foreign(Subscription.fk_student_id)",
                                    secondaryjoin="Course.id == foreign(Subscription.fk_course_id)",
                                    viewonly = True)
    def to_dict(self):
        return dict(
            id=self.id,
            username=self.username,
            role=self.role,
        )

    def get_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS512')

    @staticmethod
    def verify_reset_token(token):
        try:
            _id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS512'])['reset_password']
        except:
            return
        return User.query.get(_id)


class Session(db.Model):
    __tablename__="session"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50))
    start_date = db.Column(db.Date, default = datetime.utcnow())
    end_date = db.Column(db.Date, default = datetime.utcnow())
    is_active = db.Column(db.Boolean, default = True)
    is_disabled = db.Column(db.Boolean, default = False)
    # languages = db.relationship('Language', backref="session_languages", lazy="subquery")
    courses = db.relationship('Course', backref="session_courses", lazy="subquery")
    def __repr__(self):
        return f'{self.label}'


class Language(db.Model):
    __tablename__="language"
    id = db.Column(db.Integer, primary_key = True)
    label = db.Column(db.String(100))
    levels = db.relationship('Level', secondary = "language_level",
                             primaryjoin="Language.id == foreign(LanguageLevel.fk_language_id)",
                             secondaryjoin="Level.id==foreign(LanguageLevel.fk_level_id)",
                             viewonly=True)
    def __repr__(self):
        return f'{self.label}'


class Subscription(db.Model):
    __tablename__="subscription"
    id = db.Column(db.Integer, primary_key = True)
    fk_student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fk_course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    is_waiting = db.Column(db.Boolean, default = False)
    subscription_date = db.Column(db.DateTime, default = datetime.utcnow())
    charges_paid = db.Column(db.Boolean, default = False)


class Note(db.Model):
    __tablename__="note"
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fk_level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    fk_language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    mark = db.Column(db.Float, default = 0)


class LanguageLevel(db.Model):
    __tablename__="language_level"
    id = db.Column(db.Integer, primary_key=True)
    fk_level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    fk_language_id = db.Column(db.Integer, db.ForeignKey('language.id'))


class CourseLanguage(db.Model):
    __tablename__="course_language"
    id = db.Column(db.Integer, primary_key = True)
    fk_level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    fk_language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    fk_course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


@login.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

