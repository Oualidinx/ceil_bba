import datetime

from flask import flash, redirect, render_template, url_for, session, request, abort, make_response
from root import database
from root.admin import admin_bp
from root.models import Category, Course, CourseLanguage, Session, User, Subscription,LogsUserPrice \
                        ,Language, Level
from root.forms import CategoryForm,AddCourseForm, SessionForm, EditCategoryForm,EnableSubscription, EditCourseForm, LanguageForm, EditLanguageForm
import bleach
import pandas as pd
from flask_login import login_required, current_user
from sqlalchemy.sql import and_
ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'dt', 'dd', 'table', 'tbody', 'thead',
                                      'section',
                                      'u', 'i', 'br', 'em', 'strong', 'p', 't']


@admin_bp.before_request
def admin_before_request():
    session['actual_role'] = "master"


@admin_bp.get('/')
@admin_bp.post('/')
@login_required
def index():
    _session = Session.query.all()
    if not _session:
        year = datetime.datetime.utcnow().year
        _session = Session(label = f'{year}/{year + 1}')
        database.session.add(_session)
        database.session.commit()
    form = EnableSubscription()
    _session = Session.query.all()[-1]
    if request.method == "GET":

        if _session.is_disabled:
            form.enable.data = "f"
        else:
            form.enable.data = "o"
    if form.validate_on_submit():
        _session.is_disabled = True if form.enable.data =="f" else False
        database.session.add(_session)
        database.session.commit()
        flash('Information sont à jour!', 'success')
        return redirect(url_for("admin_bp.index"))
    return render_template("master_dashboard.html", form = form, _session = _session)


@admin_bp.get('/category/new')
@admin_bp.post('/category/new')
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category()
        category.label = form.label.data
        category.price = float(form.price.data)
        database.session.add(category)
        database.session.commit()
        flash('Catégorie ajoutée avec succès',"success")
        return redirect(url_for('admin_bp.new_category'))
    return render_template('add_category.html', form = form)


@admin_bp.get('/formation')
@admin_bp.post('/formation')
@login_required
def formation():
    courses =[obj.to_dict() for obj in Course.query.all()]
    return render_template('formation.html', courses=courses)



@admin_bp.get('/formation/new')
@admin_bp.post('/formation/new')
@login_required
def new_course():
    form = AddCourseForm()
    _session = Session.query.all()[-1]
    session_form = SessionForm()
    if form.validate_on_submit():
        course = Course()
        course.label = form.label.data
        # course.on_test = form.on_test.data
        course.fk_session_id = _session.id
        if form.price.data:
            course.price = float(form.price.data)
        cleaned_data = bleach.clean(form.description.data, tags=ALLOWED_TAGS)
        course.description = cleaned_data
        database.session.add(course)
        database.session.commit()
        # level_language = LanguageLevel()
        # level_language.fk_level_id = int(form.level.data)
        # level_language.fk_language_id = int(form.language.data)
        # database.session.add(level_language)
        # database.session.commit()
        course_language = CourseLanguage()
        course_language.limit_number = int(form.limit_number.data)
        course_language.fk_course_id = course.id
        course_language.fk_language_id = int(form.language.data.id)
        course_language.fk_level_id = form.level.data.id
        database.session.add(course_language)
        database.session.commit()
        flash('Ajout avec succès', "success")
        return redirect(url_for('admin_bp.new_course'))
    return render_template('new_course.html', form = form, session_form = session_form)


@admin_bp.get('/session/new')
@admin_bp.post('/session/new')
@login_required
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
@login_required
def students(course_id, session_id):
    _session = Session.query.get(session_id)
    session['session_id'] = session_id
    session['next']="admin_bp.students"
    if not _session:
        flash('Aucune session n\'est trouvée', 'warning')
        return redirect(url_for('admin_bp.formation'))
    course = Course.query.filter_by(fk_session_id = session_id).filter_by(id = course_id).first()
    if not course:
        flash('Formation introuvable','danger')
        return redirect(url_for('admin_bp.formation'))
    # liste = [obj.to_dict().update(status = Subscription.query.filter(and_(Subscription.fk_student_id == obj.id,
    #                                                                       Subscription.fk_course_id == course.id))) \
    #                                                         .first().is_accepted for obj in course.students]
    liste = [Subscription.query.filter(
                                  and_(Subscription.fk_student_id == obj.id, Subscription.fk_course_id == course.id)) \
                                                            .first().repr() for obj in course.students]
    # print(liste)
    return render_template('students.html', formation = course, students = liste)


@admin_bp.get('/students/get/<int:student_id>')
@login_required
def get_student(student_id):
    student = User.query.get(student_id)
    if not student:
        abort(404)
    subscriptions = Subscription.query.filter_by(fk_student_id = student_id).all()
    subscriptions=[obj.to_dict() for obj in subscriptions]
    return render_template('student_info.html',
                           student = student.details(),
                           subscriptions = subscriptions)



@admin_bp.get('/students/accept/<int:student_id>/<int:course_id>')
@login_required
def accept(student_id, course_id):
    student = User.query.get(student_id)
    if not student:
        flash('Impossible de trouver cet étudiant','danger')
        return redirect(url_for(session['next'], course_id=course_id, session_id=session['session_id'])) if 'session_id' in session else redirect(url_for(session['next']))
    subscription = Subscription.query.filter(and_(Subscription.fk_student_id == student_id, Subscription.fk_course_id == course_id)).first()
    if subscription and subscription.is_waiting and subscription.is_accepted == -1:
        subscription.is_waiting = False
        subscription.is_accepted = 1
        subscription.note = "Félicitations, vous avez été accepté pour continue les démarches d'inscription pour ce cours."
        database.session.add(subscription)
        database.session.commit()
    else:
        flash('Impossible de changé le status', 'danger')
        return redirect(url_for(session['next'], course_id=session['course_id'], session_id=session[
            'session_id'])) if 'course_id' in session and 'session_id' in session else redirect(
            url_for(session['next']))
    flash('Operation a terminée avec succès', 'success')
    return redirect(url_for('admin_bp.get_student',
                            student_id = student_id))


@admin_bp.get('/students/denies/<int:student_id>/<int:course_id>')
@login_required
def denies(student_id, course_id):
    student = User.query.get_or_404(student_id)
    if not student:
        flash('Impossible de trouver cet étudiant', 'danger')
        return redirect(url_for(session['next'], course_id=course_id,
                                session_id=session['session_id'])) if 'session_id' in session else redirect(
            url_for(session['next']))
    subscription = Subscription.query.filter(and_(Subscription.fk_student_id == student_id, Subscription.fk_course_id == course_id)).first()
    # subscription = Subscription.query.filter_by(fk_student_id = student.id).first()
    if subscription and subscription.is_waiting and subscription.is_accepted == -1:
        subscription.is_waiting = False
        subscription.is_accepted = -1
        subscription.note = "Vous n'êtes légible pour poursuivre les démarches d'inscription pour suivre le cours"
        database.session.add(subscription)
        database.session.commit()
    else:
        flash('Impossible de changé le status', 'danger')
        return redirect(url_for(session['next'], course_id=session['course_id'], session_id=session[
            'session_id'])) if 'course_id' in session and 'session_id' in session else redirect(
            url_for(session['next']))
    flash('Operation a terminée avec succès', 'success')
    return redirect(url_for('admin_bp.get_student', student_id = student.id))


@admin_bp.get('/category/<int:category_id>/edit')
@admin_bp.post('/category/<int:category_id>/edit')
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    previous_value = category.price
    form = EditCategoryForm()
    if request.method=="GET":
        form.label.data = category.label
        form.price.data = category.price

    if form.validate_on_submit():
        category.price = float(form.price.data)
        category.label = form.label.data
        database.session.add(category)
        database.session.commit()
        log = LogsUserPrice()
        log.fk_category_id = category_id
        # log.updated_by = current_user.id
        log.previous_value = previous_value
        database.session.add(log)
        database.session.commit()
        flash('Categorie a été modifiée avec succès','success')
        return redirect(url_for('admin_bp.categories'))
    return render_template('edit_category.html', form = form)


@admin_bp.get('/category/list')
@login_required
def categories():
    liste = Category.query.all()
    list_categories = [obj.to_dict() for obj in liste]
    return render_template('categories.html', liste = list_categories)


@admin_bp.get('/course/<int:course_id>/list')
@login_required
def get_students(course_id):
    course = Course.query.get(course_id)
    if not course:
        abort(404)
    users = []
    if course.students:
        users = [obj.repr(['id','first_name','last_name', 'email', 'course_label', 'course_day', 'course_periode']) for obj in Subscription.query.filter_by(fk_course_id = course_id).all()]
        # print(users)
    df = pd.DataFrame(users, columns=['Numéro','Nom' ,'Prénom','Email','La formation','Jour','Période'])
    response = make_response(df.to_csv())
    response.headers['Content-Disposition'] = f"attachment; filename=list_etudiants_{Course.query.get(course_id).label}.csv"
    response.headers['Content-Type'] = "text/csv"
    return response


@admin_bp.get('/formation/<int:course_id>/edit')
@admin_bp.post('/formation/<int:course_id>/edit')
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if not course:
        flash('Formation introuvable',"danger")
        return redirect(url_for('admin_bp.formation'))
    course_language = CourseLanguage.query.filter_by(fk_course_id = course_id).first()
    if not course_language:
        flash('Certain informations sont mal enregistrées','danger')
        return redirect(url_for('admin_bp.formation'))
    form = EditCourseForm(
        language=Language.query.get(course_language.fk_language_id),
        level=Level.query.get(course_language.fk_level_id)) # session=Session.query.get(Course.query.get(course_id).fk_session_id),
    if request.method=="GET":
        form.label.data = course.label
        form.price.data = course.price
        form.description.data = course.description
        form.limit_number.data = course_language.limit_number
        # form.on_test.data = course.on_test
    if form.validate_on_submit():
        course.label = form.label.data
        if form.price.data:
            course.price = float(form.price.data)
        cleaned_data = bleach.clean(form.description.data, tags=ALLOWED_TAGS)
        course.description = cleaned_data
        # course.on_test = form.on_test.data
        course.fk_session_id = Course.query.get(course_id).fk_session_id # int(form.session.data.id)
        if course.is_disabled == True and int(form.limit_number.data) > course.limit_number:
            course.is_disabled = False
        course_language.limit_number = int(form.limit_number.data)
        database.session.add(course)
        database.session.commit()
        course_language.fk_course_id = course.id
        course_language.fk_language_id = int(form.language.data.id)
        course_language.fk_level_id = int(form.level.data.id)

        database.session.add(course_language)
        database.session.commit()
        flash('Modification avec succès', "success")
        return redirect(url_for('admin_bp.formation'))
    return render_template('update_course.html', form=form, _session=Session.query.all()[-1])


@admin_bp.route('/students/all')
@login_required
def all_students():
    session['next'] = "admin_bp.all_students"
    if 'session_id' in session:
        del session['session_id']
    liste = [obj.repr() for obj in Subscription.query.join(User, User.id == Subscription.fk_student_id).filter(User.role == "student").all()]
    return render_template('students.html', students=liste)


@admin_bp.route('/students/all_csv')
@login_required
def all_students_csv():
    users = []
    if  Subscription.query.all():
        #
        users = [obj.repr(['id','first_name','last_name','email','course_label','course_day','course_periode']) for obj in Subscription.query.join(User, User.id == Subscription.fk_student_id).filter(User.role=="student").all() if obj.is_accepted == 1]
    df = pd.DataFrame(users, columns=['Numéro','Nom' ,'Prénom','Email','La formation','Jour', 'Période'])
    response = make_response(df.to_csv())
    response.headers['Content-Disposition'] = f"attachment; filename=list_etudiants.csv"
    response.headers['Content-Type'] = "text/csv"
    return response


@admin_bp.get('/language/add')
@admin_bp.post('/language/add')
@login_required
def add_language():
    form = LanguageForm()
    if form.validate_on_submit():
        language = Language(label = form.label.data)
        database.session.add(language)
        database.session.commit()
        flash('Langue ajoutée avec succès', "success")
    return render_template('new_language.html', form = form)


@admin_bp.get('/language/<int:language_id>/edit')
@admin_bp.post('/language/<int:language_id>/edit')
@login_required
def edit_language(language_id):
    form = EditLanguageForm()
    l = Language.query.get(language_id)
    if not l:
        abort(404)
    if request.method == "GET":
        form.label.data = l.label
    if form.validate_on_submit():
        l = form.label.data
        database.session.add(l)
        database.session.commit()
        flash('Mise à jour avec succès')
        redirect(url_for('admin_bp.languages'))
    return render_template('new_language.html', form = form)


@admin_bp.get('/languages')
@login_required
def languages():
    _languages = [obj.to_dict() for obj in Language.query.all()]
    return render_template('languages.html', liste = _languages)



