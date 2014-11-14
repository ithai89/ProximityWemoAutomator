from flask import Flask, jsonify
from wemokit.wemo import Wemo
from json import dumps
from threading import Thread
from time import sleep

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
    thread = Thread(target=client.scan)
    thread.start()
    thread.join()
    sleep(10)
    thread.exit()
    #client.scan()
    return 'working'


@app.route("/devices/on")
def onAll():
    return jsonify(devices=str(client.onAll()))


@app.route("/devices/off")
def offAll():
    return jsonify(devices=str(client.offAll()))


@app.route("/device/<int:device_id>")
def get(device_id):
    return jsonify(devices=client.get(device_id).serialize())


@app.route("/devices/toggle")
def toggleAll():
    client.toggleAll()
    return jsonify(devices=str(client.toggleAll()))


@app.route("/device/<int:device_id>/toggle")
def toggle(device_id):
    return dumps(client.toggle(device_id).serialize())


@app.route("/device/<int:device_id>/on")
def on(device_id):
    return dumps(client.on(device_id).serialize())


@app.route("/device/<int:device_id>/off")
def off(device_id):
    return dumps(client.off(device_id).serialize())

if __name__ == '__main__':
    client = Wemo()
    print client
    client.scan()
    app.run(debug=True, port=8080, host='0.0.0.0')
