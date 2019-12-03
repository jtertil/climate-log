from flask import Flask, request
app = Flask(__name__)

fake_data = {}
fake_auth = {'sensor1': 'QYZ'}


@app.route('/')
def index():
    return 'flask run ok'


@app.route('/data/<string:sensor>')
def data(sensor):
    try:
        return fake_data[sensor]
    except KeyError:
        return f'no such sensor: {sensor}'


@app.route('/log/', methods=['POST'])
def log():
    req_data = request.get_json()
    sensor = req_data['sensor']

    if req_data['key'] == fake_auth[sensor]:
        fake_data[sensor] = (req_data['values'])

    return '1'
