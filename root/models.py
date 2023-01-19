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
    description = db.Column(db.String(2500))
    students = db.relationship('User', secondary="subscription",
                               primaryjoin = "Course.id == foreign(Subscription.fk_course_id)",
                               secondaryjoin="User.id == foreign(Subscription.fk_student_id)",
                               viewonly = True
                               )

    def to_dict(self):
        return dict(
            id = self.id,
            label = self.label,
            status = ('Désactivé','#e06000') if self.is_disabled else ("Activé", '#007256'),
            session=Session.query.get(self.fk_session_id).label,
            session_id=self.fk_session_id
        )

    def __repr__(self):
        return f'{self.label}'


class LogsUserPrice(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fk_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    previous_value = db.Column(db.Float, default = 0)
    last_modification = db.Column(db.DateTime, default=datetime.utcnow())
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'category={Category.query.get(self.fk_category_id).label}, \
                 current value = {Category.query.get(self.fk_category_id).price}, \
                 previous value = {self.previous_value}'


class Category(db.Model):
    __tablename__="category"
    id = db.Column(db.Integer, primary_key = True)
    label = db.Column(db.String(100))
    price = db.Column(db.Float, default = 0)
    price_letters = db.Column(db.String(1500))
    students = db.relationship('User', backref="category_students", lazy="subquery")

    def __repr__(self):
        return f'{self.label}'

    def to_dict(self):
        return dict(
            id = self.id,
            label = self.label,
            price = self.price
        )


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
    birthplace = db.Column(db.String(100))
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

    def details(self):
        return dict(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
            # birthday = self.birthday.date()
        )

    def detail_course(self):
        if self.courses:
            return [(self.id,self.first_name, self.last_name, self.email,obj.label) for obj in self.courses]

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
    # levels = db.relationship('Level', secondary = "language_level",
    #                          primaryjoin="Language.id == foreign(LanguageLevel.fk_language_id)",
    #                          secondaryjoin="Level.id==foreign(LanguageLevel.fk_level_id)",
    #                          viewonly=True)
    def __repr__(self):
        return f'{self.label}'

    def to_dict(self):
        return dict(
            id = self.id,
            label = self.label
        )


class Subscription(db.Model):
    __tablename__="subscription"
    id = db.Column(db.Integer, primary_key = True)
    fk_student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fk_course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    fk_payment_receipt_id = db.Column(db.Integer, db.ForeignKey('payment_receipt.id'))
    is_waiting = db.Column(db.Boolean, default = True)
    is_accepted = db.Column(db.Integer, default = -1)
    on_test = db.Column(db.Boolean, default=False)
    subscription_date = db.Column(db.DateTime, default = datetime.utcnow())
    charges_paid = db.Column(db.Boolean, default = False)
    course_day = db.Column(db.String(15))
    course_periode = db.Column(db.String(10))
    note = db.Column(db.String(1500))

    def to_dict(self):
        return dict(
            date = self.subscription_date.date(),
            course = Course.query.get(self.fk_course_id).label,
            is_waiting = self.is_waiting,
            is_accepted = self.is_accepted,
            session = Session.query.get(Course.query.get(self.fk_course_id).fk_session_id)
        )

    def repr(self, columns = None):
        all_details = dict(
            id=self.fk_student_id,
            first_name=User.query.get(self.fk_student_id).first_name,
            last_name=User.query.get(self.fk_student_id).last_name,
            birthday = User.query.get(self.fk_student_id).birthday.date() if User.query.get(self.fk_student_id).birthday else None,
            birthplace = User.query.get(self.fk_student_id).birthplace,
            email=User.query.get(self.fk_student_id).email,
            course_label = Course.query.get(self.fk_course_id).label,
            course_id=self.fk_course_id,
            course_day=self.course_day,
            course_periode = self.course_periode,
            status = 1 if (self.is_accepted == 1 or not self.on_test) else -1 if (self.is_waiting and self.is_accepted == -1)  else 0,
            note = self.note
        )
        if columns:
            return (all_details[k] for k in columns)
        return all_details

class Note(db.Model):
    __tablename__="note"
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fk_level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    fk_language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    mark = db.Column(db.Float, default = 0)


# class LanguageLevel(db.Model):
#     __tablename__="language_level"
#     id = db.Column(db.Integer, primary_key=True)
#     fk_level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
#     fk_language_id = db.Column(db.Integer, db.ForeignKey('language.id'))


class CourseLanguage(db.Model):
    __tablename__="course_language"
    id = db.Column(db.Integer, primary_key = True)
    fk_level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    limit_number = db.Column(db.Integer, default = 0)
    actual_students_number = db.Column(db.Integer, default = 0)
    fk_language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    fk_course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


@login.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

class PaymentReceipt(db.Model):
    __tablename__="payment_receipt"
    id = db.Column(db.Integer, primary_key = True)
    payment_date = db.Column(db.DateTime, default = datetime.utcnow())
    amount = db.Column(db.Float, default = 0)