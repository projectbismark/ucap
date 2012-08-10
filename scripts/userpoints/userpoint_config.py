######################################################################
###
### This script enables and disables Reward system on particular
### router
###
#####################################################################

import jsonrpclib
import os
import sys
from django.conf import settings

def print_menu():
	print 'Select a configuration (enter the number):'
	print '\t1. Enable userpoint system'
	print '\t2. Disable userpoint system'
	print '\t3. Reset userpoint system (set points to zero)'
	print '\t4. Set point per byte value'
	print '\t5. Set peak hours'
	print '\t0. Print configuration menu'
	print '\t-1. Exit'

def get_router_id(client, check_existance):
	router_id = ''
	while 1:
		router_id = raw_input("\nEnter Router ID: ")
		if router_id == '':
			print 'Empty address. Input again.'
			continue
		
		if check_existance:
			result = client.ucap.check_hid_existence(router_id)
			if result[1] == 't':
				break
			else:
				print 'This Router ID does not exist. Input again.'
				continue
		else:
			break
	
	return router_id
	
def enable_userpoint():
	client = jsonrpclib.Server('https://localhost/json/json/')
	router_id = get_router_id(client, True)
	
	try:
		res = client.ucap.enable_userpoint(router_id)
		print 'Enable userpoint...'
		print res
	except:
		print 'JSONRPC Failed. Abort'
	
def disable_userpoint():
	client = jsonrpclib.Server('https://localhost/json/json/')
	router_id = get_router_id(client, True)
	
	try:
		res = client.ucap.disable_userpoint(router_id)
		print 'Disable userpoint...'
		print res
	except:
		print 'JSONRPC Failed. Abort'
	
def reset_userpoint():
	client = jsonrpclib.Server('https://localhost/json/json/')
	router_id = get_router_id(client, True)
	res = client.ucap.reset_userpoint(router_id)
	print 'Reseting userpoint...'
	print res
	
def set_pointperbyte():
	client = jsonrpclib.Server('https://localhost/json/json/')
	router_id = get_router_id(client, True)
	pointperbyte = 0
	while 1:
		pointperbyte = raw_input("\nEnter point per byte value: ")
		if pointperbyte == '':
			print 'Empty value. Input again.'
			continue
		else:
			break
	
	print 'Setting point per byte value...'
	try:
		res = client.ucap.set_pointperbyte(router_id, float(pointperbyte))
	except:
		res = 'Error: router_id: ' + router_id + ' ; point_per_byte: ' + pointperbyte
	print res

def set_peakhours():
	client = jsonrpclib.Server('https://localhost/json/json/')
	router_id = get_router_id(client, True)
	startpeakhour = "17:00:00"
	endpeakhour = "20:00:00"
	
	while 1:
		startpeakhour = raw_input("\nEnter start peak hour (17:00:00): ")
		if startpeakhour == '':
			print 'Empty value. Input again.'
			continue
		else:
			break
			
	while 1:
		endpeakhour = raw_input("\nEnter end peak hour (20:00:00): ")
		if endpeakhour == '':
			print 'Empty value. Input again.'
			continue
		else:
			break
	
	print 'Setting point per byte value...'
	try:
		res = client.ucap.set_peak_hours(router_id, startpeakhour, endpeakhour)
	except:
		res = 'Error: router_id: ' + router_id + ' ; start_peak_hour: ' + startpeakhour + '; end_peak_hour' + endpeakhour
	print res
	

########
# MAIN
########
def main():
	# Config Menu
	print_menu()
	while 1:
		option = raw_input("\nEnter selection (number): ")
	
		if option == '1':
			enable_userpoint()
		elif option == '2':
			disable_userpoint()
		elif option == '3':
			reset_userpoint()
		elif option == '4':
			set_pointperbyte()
		elif option == '5':
			set_peakhours()
		elif option == '0':
			print_menu()
		elif option == '-1':
			break
		else:
			print 'Unknown configuration option'

if __name__ ==  '__main__':
	main()