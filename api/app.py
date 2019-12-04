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


@app.route('/data/<int:sensor_id>')
def data(sensor_id):

    r_num = db.execute(
        'SELECT count(*) AS r_num FROM public.datalog '
        'WHERE sensor_id = :sensor_id',
        {'sensor_id': sensor_id}
    ).first()[0]

    if not r_num:
        return f'no such sensor: {sensor_id}'

    q = db.execute(
        'SELECT * FROM public.datalog '
        'WHERE sensor_id = :sensor_id '
        'ORDER BY time DESC',
        {'sensor_id': sensor_id}
    ).first()

    result = {'last read': q[1], 'total reads': r_num,
              'values': {'temperature': float(q[3]), 'humidity': float(q[4])}}

    return result


@app.route('/log/', methods=['POST'])
def log():
    req_data = request.get_json()
    sensor_id = req_data['sensor_id']

    sensor = db.execute(
        'SELECT * FROM public.register '
        'WHERE id = :sensor_id',
        {'sensor_id': sensor_id}
    ).first()

    if not sensor:
        return f'no such sensor: {sensor_id}'

    elif req_data['key'] != sensor[2]:
        return 'API key no valid'

    else:
        temperature = req_data['values']['temperature']
        humidity = req_data['values']['humidity']

        db.execute(
            'INSERT INTO public.datalog (sensor_id, value_1, value_2) '
            'VALUES (:sensor_id, :temperature, :humidity) ',
            {
                'sensor_id': sensor_id,
                'temperature': temperature,
                'humidity': humidity
             })

        db.commit()
        return 'update ok'

