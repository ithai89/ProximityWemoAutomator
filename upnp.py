import sys
import struct
import IN
from socket import *


class upnp():
	mreq = None
	port = None
	msearchHeaders = {
		'Man' : '"ssdp:discover"',
		'MX'  : '3'
	}
	DEFAULT_IP = "239.255.255.250"
	DEFAULT_PORT = 1900
	DEFAULT_domainName = "schemas-upnp-org"	
	UPNP_VERSION = '1.0'
	IFACE = None
	csock = None
	ssock = None
	VERBOSE = False
	UNIQ = True	
	
	upnpRequest = {
			"location": None,
			"server": None,
			"host" : None,
			"NT" : None,  
			"urn": None
	}


	def __init__(self, ip, port, iface):
		if self.initSockets(ip,port,iface) == False:
			print 'UPNP class initialization failed!'
			sys.exit(1)

	
	def initSockets(self,ip,port,iface):
		#protective closing of code
		if self.csock:
			self.csock.close()
		if self.ssock:
			self.ssock.close()

		if iface != None:
			self.IFACE = iface
		if not ip:
                	ip = self.DEFAULT_IP
                if not port:
                	port = self.DEFAULT_PORT
                self.port = port
                self.ip = ip

		try:
			#This is needed to join a multicast group
			#FIXME: failed to join multicast group if localare connection is gone.
			self.mreq = struct.pack("4sl",inet_aton(ip),INADDR_ANY)

			#Set up client socket
			self.csock = socket(AF_INET,SOCK_DGRAM)
			self.csock.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,2)
			
			#Set up server socket
			self.ssock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
			self.ssock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
			
			#Only bind to this interface
			if self.IFACE != None:
				print '\nBinding to interface',self.IFACE,'...\n'
				self.ssock.setsockopt(SOL_SOCKET,IN.SO_BINDTODEVICE,struct.pack("%ds" % (len(self.IFACE)+1,), self.IFACE))
				self.csock.setsockopt(SOL_SOCKET,IN.SO_BINDTODEVICE,struct.pack("%ds" % (len(self.IFACE)+1,), self.IFACE))

			try:
				self.ssock.bind(('',self.port))
			except Exception, e:
				print "WARNING: Failed to bind %s:%d: %s" , (self.ip,self.port,e)
			try:
				self.ssock.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
			except Exception, e:
				print 'WARNING: Failed to join multicast group:',e
		except Exception, e:
			print "Failed to initialize UPNP sockets:",e
			return False
		return True

	def createNewListener(self,ip,port):
		try:
			newsock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
			newsock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
			newsock.bind((ip,port))
			return newsock
		except:
			return False

	#Listen for network data
	def listen(self,size,socket):
		if socket == False:
			print 'socket == false'
			socket = self.ssock
		try:
			a = socket.recv(size)
			print 'a', a
			return a

		except:
			print 'exception'
			return False

	#Send network data
	def send(self,data,socket):

		print 'send', data, socket
		#By default, use the client socket that's part of this class
		if socket == False:
			socket = self.csock
			print self.socket
		try:
			print 'sendto', data
			print 'ip: ' + self.ip, self.port
			print socket.sendto(data,(self.ip,self.port))

			return True
		except Exception, e:
			print "SendTo method failed for %s:%d : %s" % (self.ip,self.port,e)
			return False

	def parseHeader(self,data,header):
		delimiter = "%s:" % header
		defaultRet = False

		lowerDelim = delimiter.lower()
		dataArray = data.split("\r\n")
	
		#Loop through each line of the headers
		for line in dataArray:
			lowerLine = line.lower()
			#Does this line start with the header we're looking for?
			if lowerLine.startswith(lowerDelim):
				try:
					return line.split(':',1)[1].strip()
				except:
					print "Failure parsing header data for %s" % header
		return defaultRet

	#Build request query
	def buildMsearchRequest(self, searchType, searchName):
		st = "urn:%s:%s:%s:%s" % (self.DEFAULT_domainName,searchType,searchName,self.UPNP_VERSION.split('.')[0])
		
		# request = 	"M-SEARCH * HTTP/1.1\r\n"\
		# 		"HOST:%s:%d\r\n"\
		# 		"ST:%s\r\n" % (self.ip,self.port,st)
		request = 	"M-SEARCH * HTTP/1.1\r\n"\
				"Host:%s:%d\r\n"\
				"USER-AGENT: MBP\r\n"\
				"ST:upnp:rootdevice\r\n" % (self.ip, self.port)
		for header,value in self.msearchHeaders.iteritems():
				request += header + ':' + value + "\r\n"	
		request += "\r\n" 

		print 'REQUEST', request
		
		return request

	def getTypeAndName(self, strUrn):
		try:		
			return (strUrn.split(":")[2], strUrn.split(":")[3])
		except:
			#it's rootdevice as i understand
			return (None, None)

	#Find approriate Upnp device
	def findRequest(self, data, searchType, searchName):		
		returnVal = False
		knownHeaders = {				
				'HTTP/1.1 200 OK' : 'reply',
				'NOTIFY' : 'notification'
				#'M-SEARCH' : "search"
		}

		#get message type
		for text,messageType in knownHeaders.iteritems():			
			if data.upper().startswith(text):
				#we found it!
				break
			else:
				messageType = False				

		if messageType != False:			

			actualType, actualName = self.getTypeAndName(self.parseHeader(data, "NT"))
			
			if (actualType == searchType) & (actualName == searchName):
				#collect all the data
				for dataType in self.upnpRequest.iterkeys():				
					self.upnpRequest[dataType] = self.parseHeader(data,dataType.upper())
				returnVal = True


		return returnVal

	#Actively search for UPNP devices
	def msearch(self,searchType,searchName):	
		print "Entering active search"	
		myip = '192.168.1.204' #should be localhost
			
		#Have to create a new socket since replies will be sent directly to our IP, not the multicast IP
		
		print myip, self.port
		server = self.createNewListener(myip,self.port)
		if server == False:
			print 'Failed to bind port %d' % self.port
			return


		self.send(self.buildMsearchRequest(searchType, searchName),server)
		
		count = 0
		data = ""
		while True:

			print count
			count += 1		
			# self.listen(1024, server)
			data = data + server.recv(1024)
			if data.endswith(u"\r\n"):
				print "data", data
				data = ""
			# self.findRequest(self.listen(1024,server), searchType, searchName)





	#Passively listen for UPNP NOTIFY packets
	def pcap(self, searchType, searchName):
		print 'Entering passive search mode'

		myip = '' #should be localhost
			
		#Have to create a new socket since replies will be sent directly to our IP, not the multicast IP
		server = self.createNewListener(myip,self.port)
		if server == False:
			print 'Failed to bind port %d' % self.port
			return
		count = 0
		while True:
			if self.findRequest(self.listen(1024, server), searchType, searchName): return true	


if __name__ == '__main__':
	u = upnp(None, None, None)
	u.msearch(None, None)