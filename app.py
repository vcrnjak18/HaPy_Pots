import random
import os
import io

from flask import Flask, Response, render_template, request, url_for, flash, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


from .pots_readings import get_all_pots_readings
from .temp_readings import temp_reading
from .create_fig import create_figure


basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Tajna za forme'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  'sign_in'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    about = db.Column(db.Text(1000), nullable=True)

    plants = db.relationship('Plant', backref='plants')
    
    pots = db.relationship('Pot', backref='pots')

    @property
    def password_func(self):
        raise AttributeError('Error')
    
    @password_func.setter
    def password_func(self, password_func):
        self.password = generate_password_hash(password_func)

    def verify_pass(self, password_func):
        return check_password_hash(self.password, password_func)

    def __init__(self, first_name, last_name, mail, password, username):
        self.first_name = first_name
        self.last_name = last_name
        self.mail = mail
        self.password = password
        self.username = username

class UserForm(FlaskForm):

    first_name = StringField('First name:', validators=[DataRequired()])
    last_name = StringField('Last name:', validators=[DataRequired()])
    mail = StringField('E-mail:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired(), EqualTo('password1', message='Passwords must match! Try again!')])
    password1 = PasswordField('Confirm your password:', validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    about = TextAreaField('About you:')

    submit = SubmitField('Submit!')

class PasswordForm(FlaskForm):
    mail = StringField('E-mail address:', validators=[DataRequired()])
    password_to_chk = PasswordField('Password:', validators=[DataRequired()])

    submit = SubmitField('Submit!')

class Plant(db.Model):
    __tablename__ = 'plants'

    id = db.Column(db.Integer(), primary_key=True)
    plant_name = db.Column(db.String(50), nullable=False)
    sun_low = db.Column(db.Integer(), nullable=False)
    sun_hi = db.Column(db.Integer(), nullable=False)  
    hum_low = db.Column(db.Integer(), nullable=False)
    hum_hi = db.Column(db.Integer(), nullable=False)
    salt_low = db.Column(db.Integer(), nullable=False)
    salt_hi = db.Column(db.Integer(), nullable=False)
    fert_low = db.Column(db.Integer(), nullable=False)
    fert_hi = db.Column(db.Integer(), nullable=False)

    plant_pic=db.Column(db.String(), nullable=True)

    user_id_plant = db.Column(db.Integer, db.ForeignKey('users.id'))

    pots = db.relationship('Pot', backref='pot_occupied')

class PlantForm(FlaskForm):
    plant_name = StringField('Plant name:', validators=[DataRequired()])
    sun_low = IntegerField('Lowest intensity of sunlight:', validators=[DataRequired()])
    sun_hi = IntegerField('Highest intensity of sunlight:', validators=[DataRequired()])
    hum_low = IntegerField('Lowest humidity value:', validators=[DataRequired()])
    hum_hi = IntegerField('Highest humidity value:', validators=[DataRequired()])
    salt_low = IntegerField('Lowest saltiness value:', validators=[DataRequired()])
    salt_hi = IntegerField('Highest saltiness value:', validators=[DataRequired()])
    fert_low = IntegerField('Lowest fertilizer value:', validators=[DataRequired()])
    fert_hi = IntegerField('Highest fertilizer value:', validators=[DataRequired()])

    plant_pic=FileField('Upload a plant picture:')

    submit = SubmitField('Submit!')


class Pot(db.Model):
    __tablename__ = 'pots'

    id = db.Column(db.Integer(), primary_key=True)
    pot_location = db.Column(db.String(), nullable=True)
    sun_value = db.Column(db.Integer(), nullable=False)  
    hum_value = db.Column(db.Integer(), nullable=False)
    salt_value = db.Column(db.Integer(), nullable=False)
    fert_value = db.Column(db.Integer(), nullable=False)

    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'))

    user_id_pot = db.Column(db.Integer, db.ForeignKey('users.id'))

class PotForm(FlaskForm):
    pot_location = StringField('Pot location:')
    
    submit = SubmitField('Submit!')


@app.route('/')
#@login_required
def index():
    return render_template('home/index.html')



@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = UserForm()

    if form.validate_on_submit():
        new_user=User.query.filter_by(mail=form.mail.data).first()
        if new_user is None:
            hashed_pass = generate_password_hash(form.password.data, 'pbkdf2:sha256')
            new_user = User(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                mail = form.mail.data,
                password = hashed_pass,
                username = form.username.data
                )
            db.session.add(new_user)
            db.session.commit()
            flash(f'The new user {new_user.first_name} {new_user.last_name} has registered succesfully! Please log in below.', category='success')
            return redirect(url_for('sign_in'))
        else:
            flash(f'The user with this e-mail already exists! Log in below instead!', category='success')
            return redirect(url_for('sign_in'))

    return render_template(
        'users/sign_up.html', form=form)



#region Plant routes
@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    form = PlantForm()

    if request.method == 'POST':

            new_plant=Plant.query.filter_by(user_id_plant=current_user.id).filter_by(plant_name=request.form['plant_name']).first()
            
            if new_plant is None:

                    file = request.files['plant_pic']

                    if file:
                        filename = secure_filename(file.filename)
                        pic_plant_name = str(uuid.uuid1()) + '_' + filename
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_plant_name))
                    else:
                        pic_plant_name = None

                    new_plant = Plant(
                    plant_name = request.form['plant_name'],
                    sun_low = request.form['sun_low'],
                    sun_hi = request.form['sun_hi'],
                    hum_low = request.form['hum_low'],
                    hum_hi = request.form['hum_hi'],
                    salt_low = request.form['salt_low'],
                    salt_hi = request.form['salt_hi'],
                    fert_low = request.form['fert_low'],
                    fert_hi = request.form['fert_hi'],
                    plant_pic = pic_plant_name,
                    user_id_plant = current_user.id
                    )

                    db.session.add(new_plant)
                    db.session.commit()

                    flash(f'The new plant {new_plant.plant_name} was added to Plant Base succesfully!', category='success')
                    return redirect(url_for('plant_dashboard'))
            
            else:
                    flash(f'This plant already exists in your Plant Base!', category='success')
                    form=PlantForm(formdata=None)


    return render_template('plants/add_plant.html',
    form=form)



@app.route('/plant_dashboard')
def plant_dashboard():
    plants = Plant.query.order_by(Plant.id)
    return render_template('plants/plant_dashboard.html', plants=plants)



@app.route('/plant_update/<int:id>', methods=['GET', 'POST'])
def plant_update(id):
    form = PlantForm()
    plant_to_upt = Plant.query.get_or_404(id)

    if request.method == 'POST':
        plant_to_upt.plant_name = request.form['plant_name']
        plant_to_upt.sun_low = request.form['sun_low']
        plant_to_upt.sun_hi = request.form['sun_hi']
        plant_to_upt.hum_low = request.form['hum_low']
        plant_to_upt.hum_hi = request.form['hum_hi']
        plant_to_upt.salt_low = request.form['salt_low']
        plant_to_upt.salt_hi = request.form['salt_hi']
        plant_to_upt.fert_low = request.form['fert_low']
        plant_to_upt.fert_hi = request.form['fert_hi']
        plant_to_upt.user_id_plant = current_user.id

        if (request.files['plant_pic']):
           
            plant_to_upt.plant_pic = request.files['plant_pic']
            pic_plant_filename = secure_filename(plant_to_upt.plant_pic.filename)
            pic_plant_name = str(uuid.uuid1()) + '_' + pic_plant_filename
            plant_to_upt.plant_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_plant_name))
            plant_to_upt.plant_pic = pic_plant_name

        try:
            db.session.commit()
            flash("You've updated the plant information successfully!", category ='success')
            return redirect(url_for('plant_dashboard'))
            
        except:
            flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
            return redirect(url_for('plant_dashboard'))
        
    return render_template('plants/plant_update.html',
        form=form,
        plant_to_upt=plant_to_upt,
        id=id)



@app.route('/plant_delete/<int:id>')
def plant_delete(id):
    plant_to_del = Plant.query.get_or_404(id)

    try:
        db.session.delete(plant_to_del)
        db.session.commit()
        flash(f"You've deleted the plant {plant_to_del.plant_name} successfully!", category ='success')

        return redirect(url_for('plant_dashboard'))
        
    except:
        flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
        return redirect(url_for('plant_dashboard'))



@app.route('/plant_about/<int:id>')
def plant_about(id):
    plant = Plant.query.get_or_404(id)

    return render_template('plants/plant_about.html',
        plant=plant,
        id=id)
#endregion


#region User routes
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form=PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()
        
        if user:
            if check_password_hash(user.password, form.password_to_chk.data):
                login_user(user)

                flash(f'Welcome {user.first_name} {user.last_name} to your HapPY Pots account!', category='success')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password! Try again!', category='success')
        else:
            flash('Incorrect mail! Try again!', category='success')

    return render_template('users/sign_in.html',
    form=form)



@app.route('/sign_out', methods=['GET', 'POST'])
@login_required
def sign_out():
    logout_user()
    flash('You have been successfully logged out! See you soon!', category='success')
    return redirect(url_for('sign_in'))



@app.route('/users_about')
def users_about():
    return render_template('users/users_about.html')



@app.route('/users_update', methods=['GET', 'POST'])
def users_update():
    form = UserForm()
    id = current_user.id
    user_to_upt = User.query.get_or_404(id)

    if request.method == 'POST':
        user_to_upt.first_name = request.form['first_name']
        user_to_upt.last_name = request.form['last_name']
        user_to_upt.username = request.form['username']
        user_to_upt.mail = request.form['mail']
        user_to_upt.about = request.form['about']

        try:
            db.session.commit()
            flash("You've updated your profile information successfully!", category ='success')
            return redirect(url_for('users_about'))
 
        except:
            flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
            return redirect(url_for('users_about'))
        
    return render_template('users/users_update.html',
        form=form,
        user_to_upt=user_to_upt,
        id=id)



@app.route('/users_delete')
def users_delete():
    id = current_user.id
    user_to_del = User.query.get_or_404(id)

    try:
        db.session.delete(user_to_del)
        db.session.commit()
        flash(f"You've deleted your account successfully!", category ='success')
        return redirect(url_for('index'))
        
    except:
        flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
        return redirect(url_for('users_about'))
#endregion



#region Pots routes
@app.route('/add_pot', methods=['GET', 'POST'])
def add_pot():
    form=PotForm()
    plant_to_add=Plant.query.order_by(Plant.id)

    if request.method == 'POST' and form.validate_on_submit():
            plant_chosen = request.form['plants']
            new_pot = Pot(
            pot_location = request.form['pot_location'],
            sun_value = ' ',
            hum_value = ' ',
            salt_value = ' ',
            fert_value = ' ',
            plant_id = plant_chosen,
            user_id_pot = current_user.id
            )
            db.session.add(new_pot)
            db.session.commit()

            flash(f'The new {new_pot.pot_location} pot was added to Pot Base succesfully!', category='success')
            return redirect(url_for('pot_dashboard'))

    return render_template('pots/add_pot.html',
    form=form,
    plant_to_add = plant_to_add)



@app.route('/pot_about/<int:id>')
def pot_about(id):
    pot = Pot.query.get_or_404(id)
    
    city_temp=temp_reading()

    return render_template('pots/pot_about.html',
        pot=pot,
        city_temp=city_temp,
        id=id
        )
    


@app.route('/pot_dashboard')
def pot_dashboard():
    pots = Pot.query.order_by(Pot.id)
    plants = Plant.query.all()
    city_temp=temp_reading()

    return render_template('pots/pot_dashboard.html',
        pots=pots,
        city_temp=city_temp,
        plants=plants)



@app.route('/pot_delete/<int:id>')
def pot_delete(id):
    pot_to_del = Pot.query.get_or_404(id)

    try:
        db.session.delete(pot_to_del)
        db.session.commit()
        flash(f"You've deleted the {pot_to_del.pot_location} pot successfully!", category ='success')
            
        pots = Pot.query.order_by(Pot.id)

        return redirect(url_for('pot_dashboard'))
        
    except:
        flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
        return redirect(url_for('pot_dashboard'))



@app.route('/pot_update/<int:id>', methods=['GET', 'POST'])
def pot_update(id):
    form = PotForm()
    pot_to_upt = Pot.query.get_or_404(id)
    plant_to_upt=Plant.query.order_by(Plant.id) 

    if request.method == 'POST':

        pot_to_upt.pot_location = request.form['pot_location']
        pot_to_upt.plant_id = request.form['plants']
        
        try:
            db.session.commit()
            flash("You've updated the pot information successfully!", category ='success')
            return redirect(url_for('pot_dashboard'))

        except:
            flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
            return redirect(url_for('pot_dashboard'))
        
    return render_template('pots/pot_update.html',
        form=form,
        pot_to_upt=pot_to_upt,
        plant_to_upt = plant_to_upt,
        id=id)



@app.route('/refresh/<int:id>')
def refresh(id):
    pot = Pot.query.get_or_404(id)
    
    pots_rpi = get_all_pots_readings()

    pot.sun_value = round((pots_rpi[-1]['sun_value'])*random.uniform(0.8,0.9),1)
    pot.hum_value = round((pots_rpi[-1]['hum_value'])*random.uniform(0.6,0.95),1)
    pot.salt_value = round((pots_rpi[-1]['salt_value'])*random.uniform(0.2,0.5),1)
    pot.fert_value = round((pots_rpi[-1]['fert_value'])*random.uniform(0.2,0.5),1)

    try:
        
        db.session.commit()
        flash(f"You've updated the sensors' values successfully!", category ='success')

        return redirect(url_for('pot_about', id=id))
        
    except:
        flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
        return redirect(url_for('pot_dashboard'))



@app.route('/refresh_dash')
def refresh_dash():
    pots = Pot.query.order_by(Pot.id)

    pots_rpi = get_all_pots_readings()

    for pot in pots:
        pot.sun_value = round((pots_rpi[-1]['sun_value'])*random.uniform(0.8,0.9),1)
        pot.hum_value = round((pots_rpi[-1]['hum_value'])*random.uniform(0.6,0.95),1)
        pot.salt_value = round((pots_rpi[-1]['salt_value'])*random.uniform(0.2,0.5),1)
        pot.fert_value = round((pots_rpi[-1]['fert_value'])*random.uniform(0.2,0.5),1)

    try:
        
        db.session.commit()
        flash(f"You've updated the sensors' values successfully!", category ='success')

        return redirect(url_for('pot_dashboard'))
        
    except:
        flash("Oooops! Looks like we've encountered a problem...please, try again!", category ='success')
        return redirect(url_for('pot_dashboard'))



@app.route('/plot.png/<int:id>')
def plot_png(id):
    pot = Pot.query.get_or_404(id)

    sun = pot.sun_value
    hum = pot.hum_value
    salt = pot.salt_value
    fert = pot.fert_value


    fig = create_figure(sun, hum, salt, fert)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')
#endregion



#region Error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
#endregion



if __name__ == '__main__':
    app.run(debug=True)