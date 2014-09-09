from flask import Flask
from requests import post

app = Flask(__name__)

devices_list = {0: dict(name='controller',
                        url='http://192.168.1.88:49153',
                        state=False),
                1: dict(name='lightswitch',
                        url='http://192.168.1.130:49153',
                        state=False)}


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/devices')
def getDevices():
    return str(devices_list)


@app.route('/<int:device>')
def getDeviceInfo(device):
    return str(devices_list[device])


@app.route('/<int:device>/toggle')
def toggleDevice(device):
    return _toggle(device)


def _toggle(device):
    headers = {'SOAPAction': '"urn:Belkin:service:basicevent:1#SetBinaryState"',
               'Content-Type': 'text/xml; charset="utf-8"',
               'Accept': ''}

    data = '''
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" \
    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">
                <BinaryState>%d</BinaryState>
            </u:SetBinaryState>
        </s:Body>
    </s:Envelope>''' % (0 if devices_list[device]['state'] else 1)

    r = post("%s/upnp/control/basicevent1" % (devices_list[device]['url']),
             headers=headers,
             data=data)
    print r.status_code
    if r.status_code == 200:
        devices_list[device]['state'] = not devices_list[device]['state']
    return 'Status-code: ' + str(r.status_code) + '\n' + str(r.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=51515)
