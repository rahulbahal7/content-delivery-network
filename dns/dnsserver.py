import socket
import sys
import getopt
from PrimaryServer import PrimaryServer, PrimaryRequestHandler

IP = ''
PRIMARY_SERVER_PORT=50010

# Method to parse the input and get port and cdn name
def parse_input(arg):
	port = 50000 
	name = ''
	opts, args = getopt.getopt(arg[1:], 'p:n:')
	for param, val in opts:
		if param == '-p':	# get port
			port = int(val)
		elif param == '-n':	# get cdn name
			name = val
		else:			# else exit on invalid inputs
			sys.exit("Please enter inputs as: ./dnsserver -p <port> -n <name>") 
	print port, name
	return port, name


def start_server(port, name):
	print "here"
	primary_server = PrimaryServer((IP, PRIMARY_SERVER_PORT), PrimaryRequestHandler)
	print "after"
	primary_server.start_dns_service(IP, port, name)
	print "started dns service on port, name: ", port, name
	primary_server.serve_forever()


[port, name] = parse_input(sys.argv)
start_server(port, name)
