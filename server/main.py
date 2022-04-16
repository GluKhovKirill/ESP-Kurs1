from flask import Flask, request
import json


app = Flask(__name__)


@app.route('/')
def tst():
    return 'test'


@app.route('/validate/',methods=['GET'])
def abc():
    rfid = request.args.get('rfidUID', None, type=int)
    code = request.args.get('code', None, type=float) # TODO: IMAGE NOT NUMBER!!
    station = request.args.get('stationID', None, type=str)
    print(rfid, code, station)
    if not(rfid and code and station):
        return json.dumps({'valid':False})
    print()
    return json.dumps({'valid':True})


if __name__ == '__main__':
    app.run(host='0.0.0.0')