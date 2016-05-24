from SocketServer import UDPServer, BaseRequestHandler
from SecondaryServer import NewDNSServer, RequestHandler
import SocketServer
import threading

class PrimaryRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		print "In Primart Server Handle method!"

class PrimaryServer(SocketServer.TCPServer, SocketServer.ThreadingMixIn):
	def start_dns_service(self, ip, port, dns_server_name):
		self.dns_server = NewDNSServer(('',port), RequestHandler)
		self.dns_server.name=dns_server_name
		self.dns_sever_daemon = threading.Thread(target=self.dns_server.serve_forever)
		self.dns_sever_daemon.setDaemon(True)
		self.dns_sever_daemon.start()
