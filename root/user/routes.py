from flask import url_for, request, session, render_template, flash, redirect
from flask_login import current_user, login_required
from root import database
from root.user import user_bp
from root.models import *
from root.forms import SubscriptionForm, CoursesForm
from sqlalchemy.sql import or_, and_


@user_bp.before_request
def user_before_request():
    session['actual_role'] = 'student'


@user_bp.get('/index')
@login_required
def index():
    return render_template('user_dashboard.html')

@user_bp.get('/inscrire')
@user_bp.post('/inscrire')
@login_required
def inscrire():
    form = SubscriptionForm()
    _session = Session.query.all()[-1]
    if form.validate_on_submit():
        subscription = Subscription()
        subscription.fk_course_id = int(form.course.data.id)
        subscription.fk_student_id = current_user.id
        database.session.add(subscription)
        database.session.commit()
        flash('Votre choix a été confirmer. Merci','sucsess')
        return redirect(url_for('user_bp.inscrire'))
    return render_template('subscribe.html',form = form, _session = _session)

#""""""""""""""""""""
#   Inscriptions    #
#""""""""""""""""""""
@user_bp.get('/inscrire/data')
@login_required
def subscriptions():
    courses = User.query.get(current_user.id).courses
    student_subs = [
        {
            'id':course.id,
            'label':course.label,
            'is_disabled':Subscription.query.filter(and_(Subscription.fk_course_id == course.id, Subscription.fk_student_id == current_user.id)).first.is_waiting
        } for course in courses
    ]
    return render_template('subscriptions.html', courses=student_subs)