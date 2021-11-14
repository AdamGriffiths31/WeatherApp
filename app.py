import requests
from flask import Flask, render_template, request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] =True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'KEY'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=53080f992bd3253ff4385aed0a1711bf'
    r = requests.get(url).json()
    return r


@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        weather_data.append(weather)
    return render_template('weather.html', weather_data=weather_data)

@app.route('/', methods=['POST'])
def index_post():
    errorMessage=''
    new_city = request.form.get('city')
    if new_city:
        cityExists=City.query.filter_by(name=new_city).first()
        if not cityExists:
            new_city_data=get_weather_data(new_city)
            if new_city_data['cod']==200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                errorMessage='City not found'
        else:
            errorMessage='City already exists'
    if errorMessage:
        flash(errorMessage,'error')
    else:
        flash('City added','success')
    return redirect(url_for('index_get'))

@app.route('/delete/<name>/')
def delete_city(name):
    city=City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'{city.name} deleted','success')
    return redirect(url_for('index_get'))
