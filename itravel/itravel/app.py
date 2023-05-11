from flask import Flask, render_template, Blueprint
from forms import LoginForm, RegisterForm
from database import get_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TH1S1SMYS3CR3TK3Y4D4T44N4LYS1S'
# Define the main blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    form = LoginForm()
    if form.validate_on_submit():
        # handle login here
        db = get_db()
        pass
    # Aquí puedes hacer consultas a tu base de datos
    return render_template('index.html', login_form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Aquí puedes manejar el registro de usuarios
    form = RegisterForm()
    if form.validate_on_submit():
        # handle login here
        db = get_db()
        pass
    return render_template('register.html', register_form=form)

# Register the blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
