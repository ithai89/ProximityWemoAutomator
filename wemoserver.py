from flask import Flask, jsonify
from wemokit.wemo import Wemo

app = Flask(__name__)
client = None


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/devices")
def _devices():
    return jsonify(devices=[e.serialize() for e in client.getDevices().values()])


@app.route("/scan")
def scan():
    client.scan()
    return


@app.route("/device/<int:device_id>/toggle")
def toggle(device_id):
    return jsonify(status=dict(device_id=device_id,
                               status=str(client.toggle(device_id))))


@app.route("/device/<int:device_id>/on")
def on(device_id):
    return jsonify(status=dict(device_id=device_id,
                               status=str(client.on(device_id))))


@app.route("/device/<int:device_id>/off")
def off(device_id):
    return jsonify(status=dict(device_id=device_id,
                               status=str(client.off(device_id))))

if __name__ == '__main__':
    client = Wemo()
    print client
    client.scan()
    app.run(debug=True)
