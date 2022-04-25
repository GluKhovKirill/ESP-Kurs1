# Plug
from db_handler import DBHandler
from flask import Flask, request, Response
from functools import wraps

app = Flask(__name__)


def params_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not (request.args.get("stationID", '') and request.args.get('rfidUID', '') and request.args.get(
                'code', '')):
            return Response('You must pass a stationID, rfidUID and code', status=400)
        return function(*args, **kwargs)

    return decorated_function


@app.route('/validate/', methods=['GET'])
@app.route('/validate', methods=['GET'])
@params_required
def hello_world():
    station_id, rfid, code = request.args.get("stationID"), request.args.get("rfidUID"), request.args.get("code")

    user = handler.find_user_by_rfid(rfid)
    if not user:
        return Response("Not found", status=404)


    if 1:
        return Response("Unauthorized", status=401)
    return Response("OK", status=200)


if __name__ == '__main__':
    postgres_host = ''
    handler = DBHandler(postgres_host)
    app.run(host='0.0.0.0', port=4862)
