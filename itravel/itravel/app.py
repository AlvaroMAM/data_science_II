from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_required, logout_user, login_user, current_user, UserMixin
from forms import LoginForm, RegisterForm, HomeForm, ProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from user import User
from user_logged import UserLogged
import plotly
import plotly.graph_objs as go
import json
from queries import Queries
from airline import Airline, AirlineModel
from airport import Airport, AirportModel
from bson import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TH1S1SMYS3CR3TK3Y4D4T44N4LYS1S'
# Define the main blueprint
main = Blueprint('main', __name__)

login_manager= LoginManager()
login_manager.init_app(app)

airlineObj = Airline()
airportObj = Airport()
airlines = []
airports = []

def addAirlineToFavorites(airline):
    db = get_db()
    users_collection = db.users
    fav_exists = False
    existing_user = users_collection.find_one({'EMAIL' : "mohammad3pepe@yahoo.com"})
    existing_fav = existing_user["FAVOURITES_AIRLINES"]
    for item in existing_fav:
        if str(item["id"]) == str(airline.id):
            fav_exists = True
            break
    if fav_exists is False:
        print("does not exist")
        users_collection.update_one(
            {"EMAIL": "mohammad3pepe@yahoo.com"},
            {"$push": {"FAVOURITES_AIRLINES": airline.__dict__}}
        )
    else:
        print("Already exists")

def addAirportToFavorites(airport):
    db = get_db()
    users_collection = db.users
    fav_exists = False
    existing_user = users_collection.find_one({'EMAIL' : "mohammad3pepe@yahoo.com"})
    existing_fav = existing_user["FAVOURITES_AIRPORTS"]
    for item in existing_fav:
        if str(item["id"]) == str(airport.id):
            fav_exists = True
            break
    if fav_exists is False:
        print("does not exist")
        users_collection.update_one(
            {"EMAIL": "mohammad3pepe@yahoo.com"},
            {"$push": {"FAVOURITES_AIRPORTS": airport.__dict__}}
        )
    else:
        print("Already exists")
        
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('home.html')

    # form = LoginForm(request.form)
    # if form.validate_on_submit():
    #     db = get_db()
    #     users_collection = db.users
    #     user = users_collection.find_one({'EMAIL': form.email.data})
    #     # Checking login
    #     if user and check_password_hash(user['PASSWORD'], form.password.data):
    #         # If login is correct, we redirect to /home 
    #         user_logged = UserLogged(user['EMAIL'], user['NAME'], user['SURNAME'], user['ROLE'] ,user['FAVOURITES_AIRPORTS'], user['FAVOURITES_AIRLINES'])
    #         login_user(user_logged)
    #         return redirect('/home')
    #     else:
    #         return redirect('/login')
    # else:
    #     return render_template('index.html', login_form=form)

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

@main.route('/favorites/airlines', methods=['POST'])
def favorites():
    id = request.json["id"]
    ai = airlineObj.get_all_airlines()
    for airline in ai:
        if id == str(airline.id):
            addAirlineToFavorites(airline)
            break
        
    return redirect(url_for('main.load_profile'))
    
@main.route('/favorites/airports', methods=['POST'])
def favorites_airports():
    id = request.json["id"]
    ai = airportObj.get_all_airports()
    print(id)
    for airport in ai:
        if id == str(airport.id):
            addAirportToFavorites(airport)
            break
        
    return redirect(url_for('main.load_profile'))
   
@app.route("/favorites/airlines/delete")
def deleteFavoriteAirline():
    id = request.args.get("id")
    db = get_db()
    users_collection = db.users
    query = {"EMAIL": "mohammad3pepe@yahoo.com"}
    update = {"$pull": {"FAVOURITES_AIRLINES": {"id": ObjectId(id)}}}

    # Perform the update operation
    users_collection.update_one(query, update)
    
    return redirect(url_for('main.load_profile'))

@app.route("/favorites/airports/delete")
def deleteFavoriteAirport():
    id = request.args.get("id")
    db = get_db()
    users_collection = db.users
    query = {"EMAIL": "mohammad3pepe@yahoo.com"}
    update = {"$pull": {"FAVOURITES_AIRPORTS": {"id": ObjectId(id)}}}

    # Perform the update operation
    users_collection.update_one(query, update)
    
    return redirect(url_for('main.load_profile'))

@main.route('/profile', methods=['GET', 'POST'])
def load_profile():
    airlines = airlineObj.get_all_airlines()
    airports = airportObj.get_all_airports()
    form = ProfileForm()
    if form.validate_on_submit():
        # Proceed the fields, adding or deleting airlines or airports
        pass
        return render_template('profile.html', profile_form=form, airlines=airlines, airports=airports) 
    else:
        # We load the form to add/delete favourites airlines or airports, the form to delete user, the form to update user
        db = get_db()
        users_collection = db.users

        existing_user = users_collection.find_one({'EMAIL': 'mohammad3pepe@yahoo.com'})
        
        return render_template('profile.html', profile_form=form, 
                               airlines=sorted(airlines, key=lambda x: x.airline),
                               airports=sorted(airports, key=lambda x: x.airport),
                               fav_airlines=existing_user["FAVOURITES_AIRLINES"],
                               fav_airports=existing_user["FAVOURITES_AIRPORTS"])

@main.route('/home', methods=['GET', 'POST'])
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
