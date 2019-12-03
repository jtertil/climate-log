import os


from flask import Flask, request

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Setup database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route('/')
def index():
    return 'flask run ok'


@app.route('/data/<string:name>')
def data(name):


    try:
        q = db.execute(
            'SELECT * FROM public.' + name + ' '
            'ORDER BY time DESC'
        ).first()

        d = {'last read': q[1], 'total reads': q[0],
             'values': {'temperature': float(q[2]), 'humidity': float(q[3])}}

        return d

    except Exception as e:
        return str(e)


@app.route('/log/', methods=['POST'])
def log():
    req_data = request.get_json()
    name = req_data['name']

    sensor_key = db.execute(
        'SELECT key FROM public.sensor '
        'WHERE name = :name',
        {'name': name}
    ).first()

    if not sensor_key:
        return f'no such sensor: {name}'

    elif req_data['key'] != sensor_key[0]:
        return 'API key no valid'

    else:
        temperature = req_data['values']['temperature']
        humidity = req_data['values']['humidity']

        db.execute(
            'INSERT INTO public.' + name + ' (temperature, humidity) '
            'VALUES (:temperature, :humidity) ',
            {'temperature': temperature,
             'humidity': humidity
             })

        db.commit()
        return 'update ok'

