import socket
import struct
import commands
import subprocess
from subprocess import Popen,PIPE

#Perform ping test by using ping.sh which only sends ping 
#packets till it receives a response(upto 5 packets) and respond
#to the DNS server.
def back_ping_test():
	print "running try_listen"
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('',50010))
	sock.listen(50)
	while True:
		c,addr = sock.accept()
		print "got conn, ",addr
		client_ip = c.recv(1024)
		print client_ip
		res = subprocess.check_output(['./ping.sh',str(client_ip)])
		print res
		c.send(res)
		c.close()
back_ping_test()
