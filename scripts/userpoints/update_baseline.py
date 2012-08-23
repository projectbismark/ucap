import jsonrpclib
import os
import sys
import time
import datetime
from django.conf import settings

##############################################
# This script should be run on monthly basis
##############################################

def log(message):
	now = datetime.datetime.today()
	sdate = now.strftime("%Y-%m-%d %H:%M:%S")
	snow = now.strftime("%Y_%m_%d")
	filename = '/tmp/ucaplog/update_baseline_' + snow + '.log'
	f = open(filename, 'a')
	f.write(sdate + '\t')
	f.write(message)
	f.write('\n')
	f.close()

def get_userpoint_enabled_households(client):
	res = client.ucap.get_userpoint_enabled_households()
	return res

def get_baseline(client, house_id):
	# Definition: Baseline is the average peak hour usage
	# of the last month
	res = client.ucap.get_peak_hours_usage(house_id,1)
	peakUsage = res['total_usage']
	numOfDays = res['num_of_days']
	averagePeakUsage = peakUsage / numOfDays
	return averagePeakUsage

def update_baseline(client, house_id, baseline):
	res = client.ucap.set_peak_hours_baseline(house_id, baseline)
	return res

########
# MAIN
########

def main():
	client = jsonrpclib.Server('https://localhost/json/json/')
	households = get_userpoint_enabled_households(client)
	for household in households:
		baseline = get_baseline(client, household)
		message = 'Baseline for ' + household + ' : ' + str(baseline)
		print message
		log(message)
		
		res = update_baseline(client, household, baseline)
		print res
		log (str(res[1]))
		print '\n'

if __name__ ==  '__main__':
	main()