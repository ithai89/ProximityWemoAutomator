import requests

# POST http://192.168.1.88:49153/upnp/control/basicevent1 HTTP/1.1
# Host: 192.168.1.204
# SOAPAction: "urn:Belkin:serviceId:basicevent1#SetBinaryState"
# Content-Type: text/xml; charset="utf-8"
# Content-Length: 1024

headers = {'SOAPAction':'"urn:Belkin:service:basicevent:1#SetBinaryState"',
			   'Content-Type':'text/xml; charset="utf-8"',
			   'Accept': ''}

data = '''
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
	<s:Body>
		<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">
			<BinaryState>0</BinaryState>
		</u:SetBinaryState>
	</s:Body>
</s:Envelope>'''

r = requests.post("http://192.168.1.88:49153/upnp/control/basicevent1", headers=headers,data=data)
print r.status_code
print r.text
# Content-Type: application/soap+xml; charset-utf-8
