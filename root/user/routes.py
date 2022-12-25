from flask import url_for, request, session, render_template, flash, redirect,abort
from flask_login import current_user, login_required
from root import database
from root.user import user_bp
from root.models import *
from root.forms import SubscriptionForm, CoursesForm
from sqlalchemy.sql import or_, and_
from flask_weasyprint import HTML, render_pdf

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
    if request.method=="GET" and _session.is_disabled == True:
        flash("L'inscription n'est pas encore disponible","warning")
        return render_template('subscribe.html', form=form, _session=_session)
    if form.validate_on_submit():
        course_language = CourseLanguage.query.filter_by(fk_course_id=form.course.data.id).first()
        if (course_language.limit_number - course_language.actual_students_number)<=0:
            flash('Vous tentez d\'inscrire dans une formation dont elle est complète')
            return redirect(url_for('user_bp.inscrire'))
        subscription = Subscription()
        subscription.fk_course_id = int(form.course.data.id)
        subscription.fk_student_id = current_user.id
        database.session.add(subscription)
        database.session.commit()
        course_language.actual_students_number = course_language.actual_students_number+1
        database.session.add(course_language)
        database.session.commit()
        flash('Votre choix a été confirmer. Merci','success')
        flash('Veuillez imprimer le reçu de paiement à payer au niveau du centre. Merci', 'info')
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
            'is_disabled':Subscription.query.filter(and_(Subscription.fk_course_id == course.id,
                                                         Subscription.fk_student_id == current_user.id)).first.is_waiting
        } for course in courses
    ]
    return render_template('subscriptions.html', courses=student_subs)


@user_bp.route('/subscription/<int:receipt_id>/print', methods=['GET','POST'])
# @login_required
def print_receipt(receipt_id):
    subscription = Subscription.query.get_or_404(receipt_id)
    student = User.query.get_or_404(subscription.fk_student_id)
    if student.role!='student':
        abort(403)
    cost = Category.query.get_or_404(student.fk_category_id)
    date = subscription.subscription_date
    _session = Session.query.get_or_404(Course.query.get(subscription.fk_course_id).fk_session_id)
    html = render_template('payment_receipt.html', student = student,
                           cost = cost.price, cost_letters =  cost.price_letters,
                           date = date, _session = _session, number = receipt_id)
    return render_pdf(HTML(string=html))