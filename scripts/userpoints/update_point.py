import jsonrpclib
import os
import sys
import time
import datetime
from django.conf import settings

############################################
# This script should be run on daily basis
############################################

def log(message):
	now = datetime.datetime.today()
	sdate = now.strftime("%Y-%m-%d %H:%M:%S")
	snow = now.strftime("%Y_%m_%d")
	filename = '/tmp/ucaplog/update_point_' + snow + '.log'
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

def get_peakhours_usage(client, house_id):
	now = datetime.datetime.today()
	delta = datetime.timedelta(days=1)
	now = now - delta	
	snow = now.strftime("%Y-%m-%d")
	
	message = 'Date: ' + snow
	print message
	log(message)
	
	usage = client.ucap.get_peak_hours_usage_on_day(house_id, snow)
	return usage
	
def get_pointperbyte(client, house_id):
	res = client.ucap.get_pointperbyte(house_id)
	return float(res)

def calculate_point(client, baseline, usage, pointperbyte):
	point = 0
	delta = baseline - usage
	if delta > 0:
		point = delta * pointperbyte
	return point
	
def add_point(client, house_id, point):
	point = int(point)
	res = client.ucap.add_userpoint(house_id, point)
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
		
		peakhours_usage = get_peakhours_usage(client, household)
		message = 'Peak-hour usage for ' + household + ' : ' + str(peakhours_usage)
		print message
		log(message)
		
		pointperbyte = get_pointperbyte(client, household)
		point = calculate_point(client, baseline, peakhours_usage, pointperbyte)
		message = 'Total point for today: ' + str(point)
		print message
		log(message)
		
		res = add_point(client, household, point)
		message = 'Total accumulative points for ' + household + ' : ' + str(res)
		print message
		log(message)
		

if __name__ ==  '__main__':
	main()