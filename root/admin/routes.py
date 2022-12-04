from flask import flash, redirect, render_template, url_for, session, request, abort
from root import database
from root.admin import admin_bp
from root.models import Category, Course, CourseLanguage, LanguageLevel,Session, User, Subscription
from root.forms import CategoryForm,AddCourseForm, SessionForm, EnableSubscription
import bleach
from flask_login import login_required
from sqlalchemy.sql import and_
ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'dt', 'dd', 'table', 'tbody', 'thead',
                                      'section',
                                      'u', 'i', 'br', 'em', 'strong', 'p', 't']


@admin_bp.before_request
def admin_before_request():
    session['actual_role'] = "master"


@admin_bp.get('/')
@admin_bp.post('/')
# @login_required
def index():
    _session = Session.query.all()[-1]
    form = EnableSubscription()
    if request.method == "GET":
        form.enable.data = _session.is_disabled
    if form.validate_on_submit():
        _session.is_disabled = form.enable.data
        database.session.add(_session)
        database.session.commit()
        flash('Information sont à jour!', 'success')
        return redirect(url_for("admin_bp.index"))
    return render_template("master_dashboard.html", form = form, _session = _session)

@admin_bp.get('/category/new')
@admin_bp.post('/category/new')
# @login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category()
        category.label = form.label.data
        database.session.add(category)
        database.session.commit()
        flash('Catégorie ajoutée avec succès',"success")
        return redirect(url_for('admin_bp.new_category'))
    return render_template('add_category.html', form = form)


@admin_bp.get('/formation')
@admin_bp.post('/formation')
# @login_required
def formation():
    courses =[obj.to_dict().update({
        'link': url_for('admin_bp.students', course_id = obj.id, session_id = Session.query.all()[-1])
    }) for obj in Course.query.all()]

    return render_template('formation.html', courses=courses)



@admin_bp.get('/formation/new')
@admin_bp.post('/formation/new')
# @login_required
def new_course():
    form = AddCourseForm()
    session_form = SessionForm()
    if form.validate_on_submit():
        course = Course()
        course.label = form.label.data
        course.on_test = form.on_test.data
        course.fk_session_id = int(form.session.data)
        course.price = float(form.price.data)
        cleaned_data = bleach.clean(form.description.data, tags=ALLOWED_TAGS)
        course.description = cleaned_data
        database.session.add(course)
        database.session.commit()
        level_language = LanguageLevel()
        level_language.fk_level_id = int(form.level.data)
        level_language.fk_language_id = int(form.language.data)
        database.session.add(level_language)
        database.session.commit()
        course_language = CourseLanguage()
        course_language.fk_course_id = course.id
        course_language.fk_language_id = int(form.language.data)
        course_language.fk_level_id = int(form.level.data)
        flash('Ajout avec succès', "success")
        return redirect(url_for('admin_bp.new_course'))
    return render_template('new_course.html', form = form, session_form = session_form)


@admin_bp.get('/session/new')
@admin_bp.post('/session/new')
# @login_required
def new_session():
    session_form = SessionForm()
    if session_form.validate_on_submit():
        _session = Session()
        _session.label = session_form.label.data
        database.session.add(_session)
        database.session.commit()
        flash('Session ajoutée', 'success')
        return redirect(url_for('admin_bp.new_course'))
    return render_template('new_course.html',form = AddCourseForm(), session_form = session_form)


@admin_bp.get('/students/<int:course_id>/<int:session_id>')
# @login_required
def students(course_id, session_id):
    _session = Session.query.get(session_id)
    if not _session:
        flash('Aucune session n\'est trouvée', 'warning')
        return redirect(url_for('admin_bp.formation'))
    course = Course.query.filter_by(session_id = session_id).filter_by(id = course_id).first()
    liste = [obj.to_dict().update(status = Subscription.query.filter(and_(Subscription.fk_student_id == obj.id, Subscription.fk_course_id == course.id))).first().is_accepted for obj in course.students]
    return render_template('students.html', formation = course.label, students = liste)



