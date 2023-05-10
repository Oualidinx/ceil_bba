from flask import url_for, request, session, render_template, flash, redirect,abort
from flask_login import current_user, login_required
from root import database
from root.user import user_bp
from root.models import *
from root.forms import SubscriptionForm
from sqlalchemy.sql import or_, and_
from flask_weasyprint import HTML, render_pdf


@user_bp.before_request
def user_before_request():
    _session = Session.query.all()[-1]
    if not _session.is_disabled and _session.end_date < datetime.now():
        _session.is_disabled = True
        database.session.add(_session)
        database.session.commit()

    _session = Session.query.all()[-1]
    if _session is not None and _session.is_disabled == False:
        for course in _session.courses:
            course_language = CourseLanguage.query.filter_by(fk_course_id=course.id).first()
            if course_language and (course_language.limit_number - course_language.actual_students_number) <= 0 \
                    and course.is_disabled == False:
                course.is_disabled = True
                database.session.add(course)
                database.session.commit()
    session['actual_role'] = 'student'


@user_bp.get('/index')
@login_required
def index():
    if 'endpoint' in session:
        del session['endpoint']
    return render_template('user_dashboard.html')

@user_bp.get('/inscrire')
@user_bp.post('/inscrire')
@login_required
def inscrire():
    session['endpoint'] = 'user'
    form = SubscriptionForm()
    _session = Session.query.all()[-1]
    if not _session:
        flash('Pas de formations/sessions pour le moment','info')
        return redirect(url_for("user_bp.index"))
    if _session and _session.is_disabled == True:
        flash("L'inscription n'est pas disponible","warning")
        return redirect(url_for('user_bp.index'))
    if form.validate_on_submit():
        course_language = CourseLanguage.query.filter_by(fk_course_id=form.course.data.id).first()
        if (course_language.limit_number - course_language.actual_students_number)<=0:
            flash('Vous tentez d\'inscrire dans une formation dont elle est complète')
            return redirect(url_for('user_bp.inscrire'))
        course = Course.query.filter_by(fk_session_id = _session.id).filter_by(id = int(form.course.data.id)).first()

        subscription = Subscription.query.filter_by(fk_student_id = current_user.id) \
                    .filter(and_(Subscription.fk_course_id == course.id, Subscription.fk_student_id == current_user.id)) \
                    .first()
        receipt = PaymentReceipt()
        receipt.amount = Category.query.get(current_user.fk_category_id).price
        database.session.add(receipt)
        database.session.commit()
        if not subscription:
            subscription = Subscription()
            course_language.actual_students_number = course_language.actual_students_number + 1
        subscription.fk_course_id = int(form.course.data.id)
        subscription.fk_student_id = current_user.id
        # course = Course.query.get(int(form.course.data.id))

        if not form.course.data.on_test:
            subscription.is_waiting = False
            subscription.is_accepted = 1
            subscription.note = "Félicitations, vous avez été accepté pour continue les démarches d'inscription pour ce cours."
        else:
            level = Level.query.get(course_language.fk_level_id)
            if not level:
                print("admin_bp.inscrire ligne 54 level not found")
                abort(404)
            if level and level.label[0]=='A':
                flash('Vous ne pouvez pas passer un test de niveau A1 ou A2')
                return render_template('subscribe.html',form = form, _session = _session)
            else:
                subscription.is_waiting = True
                subscription.note = "Veuillez contacter l'administration du centre afin de fixer une date pour le teste de niveau afin de suivre ce cours"
        subscription.fk_payment_receipt_id = receipt.id
        subscription.course_day = form.jour.data
        subscription.course_periode = "Matin" if form.periode.data =="m" else "Après midi"
        database.session.add(subscription)
        database.session.commit()
        database.session.add(course_language)
        database.session.commit()
        flash('Votre choix a été confirmer. Merci','success')
        flash('Veuillez imprimer le reçu de paiement à payer au niveau du centre. Merci', 'info')
        if not form.course.data.on_test:
            return redirect(url_for('user_bp.print_receipt', receipt_id = receipt.id))
    return render_template('subscribe.html',form = form, _session = _session)


#""""""""""""""""""""
#   Inscriptions    #
#""""""""""""""""""""
@user_bp.get('/inscrire/data')
@login_required
def subscriptions():
    session['endpoint'] = 'user'
    courses = User.query.get(current_user.id).courses
    student_subs = [
        {
            'id':course.id,
            'label':course.label,
            'status':Subscription.query.filter(and_(Subscription.fk_course_id == course.id,
                                                         Subscription.fk_student_id == current_user.id)).first().repr()['status'],
            'note':Subscription.query.filter(and_(Subscription.fk_course_id == course.id,
                                                         Subscription.fk_student_id == current_user.id)).first().note,
            'payment_receipt':Subscription.query.filter(and_(Subscription.fk_course_id == course.id,
                                                         Subscription.fk_student_id == current_user.id)).first().fk_payment_receipt_id
        } for course in courses
    ]
    return render_template('subscriptions.html', courses=student_subs)

from num2words import num2words
@user_bp.route('/subscription/<int:receipt_id>/print', methods=['GET','POST'])
@login_required
def print_receipt(receipt_id):
    session['endpoint'] = 'user'
    subscription = Subscription.query.filter_by(fk_payment_receipt_id = receipt_id).first()
    if not subscription:
        abort(404)
    student = User.query.get(subscription.fk_student_id)
    if not student:
        abort(404)
    if student.role!='student':
        abort(403)
    cost = Category.query.get_or_404(student.fk_category_id)
    date = subscription.subscription_date
    total_letters = num2words(cost.price_letters.total, lang='fr') + " dinars algérien"
    _session = Session.query.get_or_404(Course.query.get(subscription.fk_course_id).fk_session_id)
    html = render_template('payment_receipt.html', student = student,
                           cost = cost.price, cost_letters =  total_letters,
                           date = date, _session = _session, number = receipt_id)
    return render_pdf(HTML(string=html))