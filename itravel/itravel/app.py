from flask import Flask, render_template, Blueprint, redirect, request, flash
from flask_login import LoginManager, login_required, logout_user, login_user
from forms import LoginForm, RegisterForm, HomeForm, ProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from user import User
from user_logged import UserLogged
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TH1S1SMYS3CR3TK3Y4D4T44N4LYS1S'
# Define the main blueprint
main = Blueprint('main', __name__)

login_manager= LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)


@main.route('/')
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        db = get_db()
        users_collection = db.users
        user = users_collection.find_one({'EMAIL': form.email.data})
        # Checking login
        if user and check_password_hash(user['PASSWORD'], form.password.data):
            # If login is correct, we redirect to /home 
            user_logged = UserLogged(user['EMAIL'], user['NAME'], user['SURNAME'], user['ROLE'] ,user['FAVOURITES_AIRPORTS'], user['FAVOURITES_AIRLINES'])
            login_user(user_logged)
            flash('You are now logged in', 'success')
            return redirect('/home')
        else:
            return render_template('index.html', login_form=form)
    else:
        return redirect('/')

@main.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        # Proceed to check the fields of the form an save user into db
        db = get_db()
        users_collection = db.users
        existing_user = users_collection.find_one({'EMAIL' : form.email.data})
        if existing_user is None:
            hashpass = generate_password_hash(form.password.data, method='sha256') 
            users_collection.insert({'NAME': form.name.data, 'SURNAME': form.surname.data, 'EMAIL': form.email.data, 'PASSWORD': hashpass, 'ROLE': 'USER', 'FAVOURITES_AIRPORTS': [], 'FAVOURITES_AIRLINES': []})
            flash('You are now registered and can log in', 'success')
            return redirect('/')
        else:
            flash('The email is already registered. Please choose a different one')
            return redirect('/register')
    else:
        #User not registered
        return render_template('register.html', register_form=form)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def load_profile ():
    form = ProfileForm
    if form.validate_on_submit():
        # Proceed the fields, adding or deleting airlines or airports
        db = get_db()
        pass
        return render_template('profile.html', profile_form=form)
    else:
        # We load the form to add/delete favourites airlines or airports, the form to delete user, the form to update user
        pass
        return render_template('profile.html', profile_form=form) 

@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = HomeForm()
    if form.validate_on_submit():
        # We apply the filters and execute the queries
        db = get_db()
        pass
    else:
        # Apply queries with favourite airports and airlines
        pass
    return render_template('home.html', register_form=form)

# Register the blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)