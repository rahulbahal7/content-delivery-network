import socket
import random
import sys
import getopt
import struct
import rtt_statistics as c_rtt
from SocketServer import UDPServer, BaseRequestHandler, ThreadingMixIn


# Class for DNS Quesitons
"""
DNS QUESTION Format

 0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 												|
| 					 QNAME 						|
| 												|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|					 QTYPE 						|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 					 QCLASS 					|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

"""
class DNSQuestion():
	def __init__(self):
		self.qtype = 1
		self.qclass = 0
		self.qname = ''		

	# Decapsulate the question from the DNS Query
	def deconstruct_question(self, packet):
		[self.qtype, self.qclass] = struct.unpack('>HH', packet[-4:])
		qname = packet[0:-4]
		self.qtype = 1
		# Convert name from DNS to regular format
		# E.g: 3www6google3com0 --> www.google.com
		index = 0
		str = []
		while True:
			length = ord(qname[index])
			if length == 0:
				break
			index += 1
			str.append(qname[index:index+length])
			index+=length
		self.question_name = '.'.join(str)
		self.qname = self.question_name
	
	def construct_query(self):
		print "domain",self.qname
		dns_query = ''.join(chr(len(l)) + l for l in self.qname.split('.'))
		dns_query+= '\x00'
		return dns_query + struct.pack(">HH", self.qtype, self.qclass) 

#Class for DNS Answer

"""
DNSAnswer
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|												|
/ 												/
/ 					NAME 						/
| 												|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 					TYPE 						|	
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 					CLASS 						|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 					TTL 						|
| 												|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 					RDLENGTH 					|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
/ 					RDATA 						/
/ 												/
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

"""
class DNSAnswer():
	def __init__(self):
		self.ans_name = 0xc00c
		self.rdata_type = 0x0001
		self.rdata_class = 0x0001
		self.ttl = 40
		self.rdlength = 4
		self.data = ''
	
	#Construct the DNS answer for the DNS Query
	def construct_answer(self, addr):
		print "constructing answer with : ", addr
		dns_answer = struct.pack(">HHHLH4s", self.ans_name, self.rdata_type,
		self.rdata_class, self.ttl, self.rdlength, socket.inet_aton(addr))
		return dns_answer
		
# Class for DNS Pakcet

"""
DNS Packet structure:
+---------------------+
| Header 			  |
+---------------------+
| Question 			  | the question for the name server
+---------------------+
| Answer 		      | Answers to the question
+---------------------+
| Authority 		  | Not used in this project
+---------------------+
| Additional 		  | Not used in this project
+---------------------+
"""

class DNSPacket():
	def __init__(self):
		self.id=random.randint(0,65535)
		self.message_fields =0
		self.qdcount = 0
		self.anscount = 0
		self.nscount = 0
		self.arcount = 0
		self.question = DNSQuestion()
		self.dns_answer = DNSAnswer()

	# Create a DNS Packet with the response
	def create_packet(self, domain, ip):
		self.message_fields = 0x8180
		self.anscount = 1
		dns_query = self.question.construct_query() 
		response = struct.pack(">HHHHHH",self.id, self.message_fields,
				self.qdcount, self.anscount, self.nscount, 
				self.arcount)
		response += dns_query
		dns_answer = self.dns_answer.construct_answer(ip)
		response += dns_answer
		return response	

	# Decapuslate the DNS Pakcet and get the DNS Question/Query
	def decapsulate_packet(self, packet):
		[self.id, self.message_fields, 
		self.qdcount, self.anscount, self.nscount, 
		self.arcount] = struct.unpack('>HHHHHH', packet[:12])
		# Get the question name
		self.question = DNSQuestion()
		self.question.deconstruct_question(packet[12:])

# Main Handler class, overriding the handle method here
class RequestHandler(BaseRequestHandler):
	def handle(self):
		# Retrieve the packet data and the socket
		data = self.request[0].strip()
		socket = self.request[1] 
		# Decapsulate the DNS Query packet
		dns_packet = DNSPacket()
		dns_packet.decapsulate_packet(data)
		# Reply if the request is of A record type and for our host
		print "Client: ",self.client_address[0]
		if self.server.name == dns_packet.question.qname:
			desired_ip = "54.88.98.7"
			#Get best replica
			status, desired_ip = self.server.send_client_ip(self.client_address[0])
			# Construct the DNS Answer Packet
			response = dns_packet.create_packet(dns_packet.question.qname, desired_ip)
			socket.sendto(response, self.client_address)
			if status == -1:	
				print "Performing ping test"
				c_rtt.replica_ping_test(self.client_address[0], desired_ip)

class NewDNSServer(ThreadingMixIn, UDPServer):
	def send_client_ip(self, client_ip_addr):
		[rtt,best_replica_ip] = c_rtt.find_http_rtt(client_ip_addr)	
		print "ip to send with rtt=-1: ",best_replica_ip
		print "rtt: ", rtt
		if rtt == -1:
			return [-1 , str(best_replica_ip)]
		else:
			print "no need to perform a ping test"
		return [0, str(best_replica_ip)]
