import getopt
import hashlib
import sys
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import subprocess
#from subprocess import subprocess,Popen,PIPE
import os
import urllib2
#import try_listen as t
from lrucache import LRUCache

class RequestHandler(BaseHTTPRequestHandler):

	#Overriding do_GET method to serve contents from local cache
	#and fetch contents from origin and store them here.
	def do_GET(self):
		print "self.port", self.port
		print "self.origin", self.origin

		print "------------LRU CACHE CAPACTIY-----------"
		print self.lrucache.max_capacity
		print "------------LRU CACHE size in GET-----------"
		print self.lrucache.size
		print "------------LRU CACHE-----------"
		print self.lrucache.cache
		print "-----------------------"

		homePages = ["","wiki","wiki/","wiki/Main_Page","wiki/Main_Page/"]

		pathAndFilename = self.path.split("/",1)[1]
		#If path is found in the replica
		if pathAndFilename in homePages:
			pathAndFilename = "wiki/Main_Page"
		serverPathAndFilename = pathAndFilename.replace("/",".")
		try:
			if serverPathAndFilename in self.lrucache.cache and self.path != "/wiki/Special:Random":
				print "-------before cache method-----------"
				self.get_from_cache(serverPathAndFilename)
			else:
				print "----------GET FROM ORIGIN--------------"
				print "self.path-------",self.path
				response = urllib2.urlopen("http://"+self.origin+":8080" + self.path)

				serverPathAndFilename = response.geturl().split("/",3)[-1].replace("/",".")
				if serverPathAndFilename in self.lrucache.cache:
					print "-------before cache method-----------"
					self.get_from_cache(serverPathAndFilename)
				else:
					print "-------before origin method-----------"
					self.get_from_origin(response, serverPathAndFilename)
		except:
			self.send_error(404,'File Not Found: %s' % self.path)
		return

	#Method to get data from cache and respond
	def get_from_cache(self, serverPathAndFilename):
		print "------------IN GET FROM CACHE------------"
		filepath = os.path.join(os.getcwd(),"cache",serverPathAndFilename)
		f = open(filepath)
		self.send_response(200)
		self.send_header('Content-type','')
		self.end_headers()
		self.wfile.write(f.read())
		f.close()
		self.lrucache.update_cache(serverPathAndFilename)

	#Get contents from the origin server
	def get_from_origin(self, response, serverPathAndFilename):
		print "-----------IN GET FROM ORIGIN-------------"
		data = response.read()
		self.send_response(200)
		self.send_header('Content-type','')
		self.end_headers()
		self.wfile.write(data)
		filepath = os.path.join(os.getcwd(),"cache",serverPathAndFilename)
		open(filepath, 'w').write(data)
		self.lrucache.add_file_to_cache(serverPathAndFilename, len(data))

# Method to parse the input and get port and origin
def parse_input(arg):
	port = 0 
	origin = ''
	opts, args = getopt.getopt(arg[1:], 'p:o:')
	for param, val in opts:
		# get port
		if param == '-p':
			port = int(val)
		# get origin
		elif param == '-o':
			origin = val
		# else exit on invalid inputs
		else:
			sys.exit("Please enter inputs as: ./httpserver -p <port> -o <origin>") 
	return port, origin

#Replica Server starts here by initializing cache and starting the HTTPserver
if __name__ == '__main__':
	[port, origin] = parse_input(sys.argv)
	print port
	print origin
	serverAddress = ('', port)
	RequestHandler.port = port
	RequestHandler.origin = origin
	cache_max_capacity = 9.9 * 1024 * 1024
	RequestHandler.lrucache = LRUCache(cache_max_capacity)
	RequestHandler.lrucache.create_cache_directory("cache")
	RequestHandler.lrucache.read_files_from_cache("cache")
	httpServer = HTTPServer(serverAddress, RequestHandler)
	print "httpServer has been created"
	httpServer.serve_forever()
