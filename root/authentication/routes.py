import os

from flask import url_for, redirect, request, render_template, flash, session,current_app
from root.authentication import auth_bp
from root.models import User
from flask_login import login_required, login_user, logout_user, current_user
from root.forms import LoginForm, RegistrationForm, RequestToken, ResetPasswordForm
from werkzeug.security import check_password_hash, generate_password_hash
from root import database
from flask_mail import Message

from root import mail
from dotenv import load_dotenv

@auth_bp.before_request
def define():
    session['title'] = "CEIL Bordj Bou Arreridj"

def send_reset_email(user):

    # token = user.get_token()
    user_name = current_app.config['MAIL_USERNAME']
    msg = Message('Password Reset Request',
                  sender=user_name,  # from domain
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: 
                         {url_for("auth_bp.reset_password", token=user.get_token(), _external=True)}
                        If you did not make this request then simply ignore this email and no changes will be made.'''
    mail.send(msg)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).filter_by(is_deleted=0).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=False)
                nex_page = request.args.get('next')
                if nex_page:
                    return redirect(nex_page)
                if user.role == "master":
                    return redirect(url_for('admin_bp.index'))
                return redirect(url_for('user_bp.index'))
            else:
                flash('Veuillez vérifier les informations', 'danger')
                return redirect(url_for('auth_bp.login'))
        else:
            flash('veuillez verifier les informations', 'danger')
            return redirect(url_for('auth_bp.login'))
    return render_template('login.html', form=form)


@auth_bp.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))


@auth_bp.get('/register')
@auth_bp.post('/register')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.birthday = form.birthday.data
        user.role = "student"
        user.fk_category_id = int(form.category.data.id)
        user.email = form.email.data
        user.password_hash = generate_password_hash(form.password.data,"sha256")
        database.session.add(user)
        database.session.commit()
        flash('Votre inscription a terminé avec succès.\nVous pouvez vous connecter afin de procèder votre inscription à une formation',"success")
        return redirect(url_for('auth_bp.login'))
    return render_template('registration.html', form = form)



@auth_bp.get('/request_token')
@auth_bp.post('/request_token')
def request_token():
    form = RequestToken()
    # if form.validate_on_submit():
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Un message a été transmis à votre email. Si Vous n\'avez aucun compte, vous ne recevez rien', 'info')
        return redirect(url_for('auth_bp.login'))
    return render_template('request_token.html', form = form)


@auth_bp.get("/reset_password/<string:token>")
@auth_bp.post("/reset_password/<string:token>")
def reset_password(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('Il y a une erreur', 'warning')
        return redirect(url_for('auth_bp.request_token'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.new_password.data, "SHA256")
        database.session.add(user)
        database.session.commit()
        flash('Votre mot de passe a été changé avec succès', 'success')
        return redirect(url_for('auth_bp.login'))
    else:
        print(form.errors)
    return render_template("reset_password.html", form=form)