from flask import url_for, redirect, request, render_template, flash, session,current_app, jsonify
from root.authentication import auth_bp
from root.models import User
from flask_login import login_required, login_user, logout_user, current_user
from root.forms import LoginForm, RegistrationForm, RequestToken, ResetPasswordForm
from werkzeug.security import check_password_hash, generate_password_hash
from root import database, mail
import json, os

@auth_bp.before_request
def define():
    session['title'] = "CEIL Bordj Bou Arreridj"

def send_reset_email(user, url, subject):
    user_name = current_app.config['MAIL_USERNAME']
    # msg.body = render_template('verify_email.html', url = url_for(url, token=user.get_token(), _external=True))
    mail.send(subject=subject,
                  sender=user_name,  # from domain
                  receivers=[user.email],
              html=f'''<head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="{url_for('static', filename='css/tailwind.min.css')}" rel="stylesheet">
    </head>
    <body>
        <div class="flex items-center justify-center min-h-screen p-5 bg-blue-100 min-w-screen">
            <div class="max-w-xl p-8 text-center text-gray-800 bg-white shadow-xl lg:max-w-3xl rounded-3xl lg:p-12">
                <p>Pour compléter Le service demandé, veuillez d'abord confirmer votre email afin d'être sûre de vous !</p>
                <p style="font-weight: bold;">Important: Vous avez que 5 minutes pour terminer ce processus</p>
                <div class="mt-4">
                    <a role="button" href="{url_for(url, token=user.get_token(300), _external=True)}" class="px-2 py-2 text-blue-200 bg-blue-600 rounded">Cliquez Ici pour confirmer votre adresse électronique</a>
                </div>
            </div>
        </div>
    </body>
    '''
              )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method=="GET":
        if 'new_reg' in session:
            del session ['new_reg']
    if form.validate_on_submit():
        user = User.query.filter_by(is_verified=True) \
                            .filter_by(is_deleted=0) \
                            .filter_by(email=form.email.data) \
                            .first()
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
                return render_template('login.html', form=form)

        else:
            flash('veuillez verifier les informations', 'danger')
            # return redirect(url_for('auth_bp.login'))
    return render_template('login.html', form=form)


@auth_bp.get('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth_bp.login'))


@auth_bp.get('/register')
@auth_bp.post('/register')
def register():
    form = RegistrationForm()
    os.chdir('root')
    os.chdir('static')
    os.chdir('uploads')
    file = open('../../static/uploads/algeria_postcodes.json','r')
    data = json.load(file)
    states = [(x['wilaya_name'], x['wilaya_code']+'-'+x['wilaya_name']) for x in data]
    states = list(dict.fromkeys(states))
    os.chdir('..')
    os.chdir('..')
    os.chdir('..')
    form.birth_state.choices = states
    if form.validate_on_submit():
        user = User()
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.birthday = form.birthday.data
        user.birth_city = form.birth_city.data
        user.birthplace = form.birth_state.data
        user.role = "student"
        user.fk_category_id = int(form.category.data.id)
        user.email = form.email.data
        user.password_hash = generate_password_hash(form.password.data,"sha256")
        database.session.add(user)
        database.session.commit()
        flash('Votre inscription a terminé avec succès. Un message a été transmis à votre adresse afin de confimer votre adresse',"success")
        send_reset_email(user, "auth_bp.verify_email",'Email verification')
        session['new_reg'] = 1
        return redirect(url_for('auth_bp.login'))
    return render_template('registration.html', form = form)

# @auth_bp.get('/cities')
# @auth_bp.post('/cities')
# def get_cities():
#     os.chdir('root')
#     os.chdir('static')
#     os.chdir('uploads')
#     file = open('../../static/uploads/algeria_postcodes.json', 'r')
#     data = json.load(file)
#     states = [(x['commune_name'], x['commune_name']) for x in data if x['wilaya_code'] == str(request.json['state'])]
#     states = list(dict.fromkeys(states))
#     states = [{'id': x[0], 'text': x[1]} for x in states]
#     os.chdir('..')
#     os.chdir('..')
#     os.chdir('..')
#     print(states)
#     response = jsonify(message=states),200
#     return response


@auth_bp.get('/request_token')
@auth_bp.post('/request_token')
def request_token():
    form = RequestToken()
    # if form.validate_on_submit():
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user, "auth_bp.reset_password", subject='Password Reset Request')
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
    return render_template("reset_password.html", form=form)


@auth_bp.get('/verify_email/<string:token>')
def verify_email(token):
    user = User.verify_reset_token(token)
    if not user:
        return render_template("404.html")
    if user.is_verified:
       return render_template("401.html")
    user.is_verified = True
    database.session.add(user)
    database.session.commit()
    flash('Email Validé vous pouvez connecter',"success")
    if 'new_reg' in session:
        del session['new_reg']
    return redirect(url_for('auth_bp.login'))
