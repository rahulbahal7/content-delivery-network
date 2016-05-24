import socket

client_dict={}
rtt_dict={}

SYDNEY = '52.63.206.143'
N_CALI = '54.193.70.31'
N_VIRG = '54.85.32.37'
OREGON = '52.38.67.246'
IRELAND = '52.51.20.200'
FRANKFURT = '52.29.65.165'
TOKYO = '52.196.70.227'
SINGAPORE = '54.169.117.213'
SYDNEY = '52.63.206.143'
SAO_PAO = '54.233.185.94'

REPLICAS=[N_CALI,N_VIRG,OREGON,IRELAND,FRANKFURT,TOKYO,SINGAPORE,SAO_PAO,SYDNEY]

#Initialize Records
def init_records(ip):
	local_rtt_dict = {}
	for replica in REPLICAS:
		local_rtt_dict[replica]=-1
	client_dict[ip]=local_rtt_dict
	print client_dict

#Method to initialize record if not present or get best RTT
def find_http_rtt(ip):
	print client_dict
	best_replica_init_rtt = 99999.9
	best_replica = N_VIRG
	check_flag = False
	#If record is present in the main map
	if ip in client_dict:
		print "present"
		rtt_record = client_dict[ip]
		print "RTT RECORD: ",rtt_record
		for replica in rtt_record:
			#If client is present and RTT is -1
			if rtt_record[replica] == -1:
				rtt = rtt_record[replica]
				return [rtt, replica]
		# Get the server with least RTT after updating them all
		for replica in rtt_record:
			print "get min RTT for that record"
			curr_rtt = float(rtt_record[replica])
			if curr_rtt < best_replica_init_rtt:
				print "current rtt is best", curr_rtt
				best_replica_init_rtt = curr_rtt
				best_replica = replica
		return [best_replica_init_rtt, best_replica]
	#Initialize record for new entry
	else:
		print "not present"
		print "ip to be init: ", ip
		init_records(ip)
		rtt_record = client_dict[ip]
		for replica in rtt_record:
                         print "rtt val: ",rtt_record[replica]
                         print replica
                         if rtt_record[replica] == -1:
                                 rtt = rtt_record[replica]
                                 return [rtt, replica]

#Method to send a request to http replica to perform a ping test
def replica_ping_test(ip, replica):
	s_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Socket Connection for RTT test
	print "replica: ",replica
	print "client IP: ", ip
	s_http.connect((replica, 50010))
	s_http.send(ip)
	output = s_http.recv(1024)
	output = output.split('\n')[-3:]
	timing_stats = output[0].split("=")[1].split("/")
	rtt = timing_stats[0]
	print "rtt: ",rtt
	rtt_record = client_dict[ip]
	#Update RTT
	if rtt_record[replica] == -1:
		rtt_record[replica]=float(rtt)
	client_dict[ip] = rtt_record
	print "after updating rtt, RTT RECORD: ", rtt_record
	print "after updating rtt: ",client_dict
	s_http.close()
