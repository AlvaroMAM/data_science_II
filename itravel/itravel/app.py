from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_required, logout_user, login_user, current_user, UserMixin
from forms import LoginForm, RegisterForm, HomeForm, ProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from user import User
from user_logged import UserLogged
import plotly
import plotly.graph_objs as go
import plotly.express as px
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

queryManager = Queries()
airlineObj = Airline()
airportObj = Airport()
airlines = []
airports = []
queriesDone = False
queriesAirportsDone = False
airlines_no_delays = []
filtered_json_arr = None
filtered_airports_json_arr = None
current_user_email = ""
get_filtered_json_arr = False

popular_airports_json = None
most_traffic_airports_json = None

checked_airlines_arr = []
checked_airports_arr = []
updated_airlines_fav = False
updated_airports_fav = False

def addAirlineToFavorites(airline):
    db = get_db()
    users_collection = db.users
    fav_exists = False
    existing_user = users_collection.find_one({'EMAIL' : current_user_email})
    existing_fav = existing_user["FAVOURITES_AIRLINES"]
    for item in existing_fav:
        if str(item["id"]) == str(airline.id):
            fav_exists = True
            break
    if fav_exists is False:
        print("does not exist")
        users_collection.update_one(
            {"EMAIL": current_user_email},
            {"$push": {"FAVOURITES_AIRLINES": airline.__dict__}}
        )
    else:
        print("Already exists")

def addAirportToFavorites(airport):
    db = get_db()
    users_collection = db.users
    fav_exists = False
    existing_user = users_collection.find_one({'EMAIL' : current_user_email})
    existing_fav = existing_user["FAVOURITES_AIRPORTS"]
    for item in existing_fav:
        if str(item["id"]) == str(airport.id):
            fav_exists = True
            break
    if fav_exists is False:
        print("does not exist")
        users_collection.update_one(
            {"EMAIL": current_user_email},
            {"$push": {"FAVOURITES_AIRPORTS": airport.__dict__}}
        )
    else:
        print("Already exists")


def getAirlinesFigures(items1, items2, items3, items4):
    # Create charts 
    fig_delays = go.Figure(data=go.Bar(x=list(map(lambda obj: str(obj["airline_name"]), items1)),
                                y=list(map(lambda obj: str(obj["avg_arrival_delay"]), items1)) 
                                ))
    fig_delays.update_layout(title='Airlines with Most Delays',xaxis_title='Airlines',
        yaxis_title='Delays', barmode='stack' )
    airlines_delays_chart_json = fig_delays.to_json()

    fig_security_delays = go.Figure(data=go.Bar(x=list(map(lambda obj: str(obj["airline_name"]), items2)),
                                y=list(map(lambda obj: str(obj["total_flights_security_delay"]), items2)) 
                                ))
    fig_security_delays.update_layout(title='Airlines with Most Number of Flights with Security Delays', xaxis_title='Airlines',
        yaxis_title='Total Number of Flights', barmode='stack' )
    airlines_security_delays_chart_json = fig_security_delays.to_json()

    fig_cancelled_flights = go.Figure(data=go.Bar(x=list(map(lambda obj: str(obj["airline_name"]), items3)),
                                y=list(map(lambda obj: str(obj["cancelled_flights_count"]), items3)) 
                                ))
    fig_cancelled_flights.update_layout(title='Airlines with Most Canceled Flights', xaxis_title='Airlines',
        yaxis_title='Canceled Flights Number', barmode='stack' )
    airlines_cancelled_flights_chart_json = fig_cancelled_flights.to_json()
    
    fig_most_travelled_distance = go.Figure(data=go.Bar(x=list(map(lambda obj: str(obj["airline_name"]), items4)),
                                y=list(map(lambda obj: str(obj["total_distance"]), items4)) 
                                ))
    fig_most_travelled_distance.update_layout(title='Airlines with Most Travelled Distance', xaxis_title='Airlines',
        yaxis_title='Total Travelled Distance', barmode='group' )
    airlines_most_travelled_distance_chart_json = fig_most_travelled_distance.to_json()
    
    
    json_arr = []
    json_arr.append(airlines_delays_chart_json)
    json_arr.append(airlines_security_delays_chart_json)
    json_arr.append(airlines_cancelled_flights_chart_json)
    json_arr.append(airlines_most_travelled_distance_chart_json)
    
    return json_arr

def getAirportsFigures(items1, items2):
    fig_popular = go.Figure(data=go.Bar(x=list(map(lambda obj: str(obj["airport_name"]), items1)),
                                y=list(map(lambda obj: str(obj["flights_count"]), items1)) 
                                ))
    fig_popular.update_layout(title='Most Popular Airports',xaxis_title='Airports',
        yaxis_title='Number of Flights', barmode='stack' )
    
    popular_airports_chart_json = fig_popular.to_json()

    # Crear listas de datos
    airports = [d['airport_name'] for d in items2]
    destination_counts = [d['destination_count'] for d in items2]
    origin_counts = [d['origin_count'] for d in items2]

    # Crear traza para 'destination_count'
    trace1 = go.Scatter(
        x=airports,
        y=destination_counts,
        mode='lines',
        name='Destination Counts',
        line=dict(color='blue')
    )

    # Crear traza para 'origin_count'
    trace2 = go.Scatter(
        x=airports,
        y=origin_counts,
        mode='lines',
        name='Origin Counts',
        line=dict(color='red')
    )

    # Agregar las trazas a la gráfica
    data = [trace1, trace2]

    # Crear el layout de la gráfica
    layout = go.Layout(
        title='Counts by Airport',
        xaxis=dict(title='Airport'),
        yaxis=dict(title='Count')
    )

    most_traffic = go.Figure(data=data, layout=layout).to_json()
    
    return popular_airports_chart_json, most_traffic

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)

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
            global updated_airlines_fav
            updated_airlines_fav = True
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
            global updated_airports_fav
            updated_airports_fav = True
            break

    return redirect(url_for('main.load_profile'))
   
@app.route("/favorites/airlines/delete")
def deleteFavoriteAirline():
    id = request.args.get("id")
    db = get_db()
    users_collection = db.users
    query = {"EMAIL": current_user_email}
    update = {"$pull": {"FAVOURITES_AIRLINES": {"id": ObjectId(id)}}}

    # Perform the update operation
    users_collection.update_one(query, update)
    
    global updated_airlines_fav
    updated_airlines_fav = True
    
    return redirect(url_for('main.load_profile'))

@app.route("/favorites/airports/delete")
def deleteFavoriteAirport():
    id = request.args.get("id")
    db = get_db()
    users_collection = db.users
    query = {"EMAIL": current_user_email}
    update = {"$pull": {"FAVOURITES_AIRPORTS": {"id": ObjectId(id)}}}

    # Perform the update operation
    users_collection.update_one(query, update)
    global updated_airports_fav
    updated_airports_fav = True
    return redirect(url_for('main.load_profile'))

@main.route('/profile', methods=['GET', 'POST'])
def load_profile():
    db = get_db()
    users_collection = db.users
    current_user_email = users_collection.find()[0]['EMAIL']
    
    airlines = airlineObj.get_all_airlines()
    airports = airportObj.get_all_airports()
    existing_user = users_collection.find_one({'EMAIL': current_user_email})
        
    return render_template('profile.html',
                            airlines=sorted(airlines, key=lambda x: x.airline),
                            airports=sorted(airports, key=lambda x: x.airport),
                            fav_airlines=existing_user["FAVOURITES_AIRLINES"],
                            fav_airports=existing_user["FAVOURITES_AIRPORTS"])

@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
def home():
    form = HomeForm()
    User.create_user()
    global current_user_email
    
    db = get_db()
    users_collection = db.users
    current_user_email = users_collection.find()[0]['EMAIL']
    existing_user = users_collection.find_one({'EMAIL': current_user_email})
    global filtered_json_arr
    global updated_airlines_fav
    global updated_airports_fav
    global queriesDone
    
    if not queriesDone:
        print("Perfrom Queries")
        queryManager.perform_airlines_queries(existing_user["FAVOURITES_AIRLINES"])
        queriesDone = True
        
    if updated_airlines_fav == True:
        queryManager.perform_airlines_queries(existing_user["FAVOURITES_AIRLINES"])
        updated_airlines_fav = False
        
    if filtered_json_arr is None: 
        json_arr = getAirlinesFigures(queryManager.airlines_delays,
                                    queryManager.airlines_security_delays,
                                    queryManager.airlines_with_cancelled_flights,
                                    queryManager.airlines_with_most_travelled_distance)
        no_delays = queryManager.airlines_no_delays
    else:
        json_arr = filtered_json_arr
        no_delays=airlines_no_delays
        
    return render_template('home.html', register_form=form,
                           fav_airlines=existing_user["FAVOURITES_AIRLINES"],
                           json_arr=json_arr,
                           airlines_no_delays=no_delays,
                           checked_airlines_arr=checked_airlines_arr)

@main.route('/airports', methods=['GET', 'POST'])
def airports():
    User.create_user()
    global current_user_email
    
    db = get_db()
    users_collection = db.users
    current_user_email = users_collection.find()[0]['EMAIL']
    existing_user = users_collection.find_one({'EMAIL': current_user_email})
    global updated_airports_fav
    global queriesAirportsDone
    
    if not queriesAirportsDone:
        print("Perfrom Queries")
        queryManager.perform_airports_queries(existing_user["FAVOURITES_AIRPORTS"])
        queriesAirportsDone = True
        
    if updated_airports_fav == True:
        queryManager.perform_airports_queries(existing_user["FAVOURITES_AIRPORTS"])
        updated_airports_fav = False
        
    global popular_airports_json
    global most_traffic_airports_json 
        
    if popular_airports_json is None:
        print("Hello 1")
        print(queryManager.popular_airports)
        popular_json, most_traffic_json = getAirportsFigures(queryManager.popular_airports,
                                               queryManager.airports_with_most_traffic)
        
    else:
        print("Hello 2")
        popular_json = popular_airports_json
        most_traffic_json = most_traffic_airports_json

    return render_template('airports.html',
                           fav_airports=existing_user["FAVOURITES_AIRPORTS"],
                           popular_airports_json=popular_json,
                           most_traffic_json=most_traffic_json,
                           checked_airports_arr=checked_airports_arr)
    
    
@main.route('/home/airlines/filter', methods=['POST'])
def filtered_home_airlines():

    global checked_airlines_arr
    
    checked_airlines_arr = request.json["ids"]

    f1, f2, f3, f4, f5 = queryManager.filter_airlines_queries(checked_airlines_arr)
    
    global filtered_json_arr
    global airlines_no_delays
    
    filtered_json_arr = getAirlinesFigures(f1,f2,f3,f4)
    airlines_no_delays = f5
    return redirect(url_for("main.home"))
    
@main.route('/home/airports/filter', methods=['POST'])
def filtered_home_airports():

    global checked_airports_arr
    
    checked_airports_arr = request.json["ids"]

    f1, f2 = queryManager.filter_airports_queries(checked_airports_arr)

    global popular_airports_json
    global most_traffic_airports_json

    popular_airports_json, most_traffic_airports_json =  getAirportsFigures(f1,f2)
        
    return redirect(url_for("main.airports"))

# Register the blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
