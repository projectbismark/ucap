import jsonrpclib
import os
import time
import pg
import sys
import time
import datetime
import shlex, subprocess
from django.conf import settings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

#######
# LIB #
#######

def get_config(key):
    config = ''
    try:
       config = open('server.conf').readlines()
    except IOError as (errno, strerror):
      print "I/O error({0}): {1}".format(errno, strerror)

    for i in config:
        i = i.replace(" ","").replace('\n','').split("=")
        if i[0] == key:
            return i[1]
    return ''

def check_for_zero(arr):
	for i in range(len(arr)):
		if arr[i] != 0:
			return False
	return True

def arr_dump(arr):
	for i in range(len(arr)):
		print arr[i]

def db_open():
	sql_host = get_config('sql_host').strip()
	sql_user = get_config('sql_user').strip()
	sql_passwd = get_config('sql_passwd').strip()
	sql_db = get_config('sql_db').strip()
	conn = pg.connect(host=sql_host, dbname=sql_db, user=sql_user, passwd=sql_passwd)
	return conn
	
def db_execute(conn, cmd):
	res = conn.query(cmd)
	return res.dictresult()
	
def get_timezone(houseid):
	conn = db_open()
	cmd = "SELECT tzone FROM households WHERE id='%s'"%(houseid)
	res = db_execute(conn, cmd)
	timezone = res[0]['tzone']
	conn.close()
	return timezone

###############
# PLOT HELPER #
###############

def array_parse_date(data, index, timezone):
	ret = []
	for datum in data:
		entry = datum[index]
		entry = datetime.datetime(*(time.strptime(entry, '%Y-%m-%d %H:%M:%S')[0:6]))
		delta = datetime.timedelta(hours=timezone)
		entry = entry + delta
		ret.append(entry)
	return ret

def array_parse_int(data, index):
	ret = []
	for datum in data:
		entry = datum[index]
		ret.append(int(entry))
	return ret

def arr_average(arr):
	ret = []
	cols = len(arr[0])
	rows = len(arr)
	for col in range(cols):
		temp = []
		for row in range(rows):
			temp.append(arr[row][col])
		#print temp
		average = np.mean(temp)
		ret.append(int(average))
	return ret
	
########
# MAIN #
########

houseid = ''
tdate = ''
period = ''
try:
	# Get command line args
	houseid = sys.argv[1]
	tdate = sys.argv[2]
	period = int(sys.argv[3])
except:
	print "Usage: " + sys.argv[0] + " house_id date period"
	print "Example: " + sys.argv[0] + " OWC43DC7B0AE78 2012-06-01 30"
	sys.exit(0)

# Parse date
one_day = datetime.timedelta(days=1)
arr_date = tdate.split('-')
idate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 0, 0, 0)

# Get data from JSONRPC
client = jsonrpclib.Server('https://localhost/json/json/')
timezone = get_timezone(houseid)
date = []
all_usage = []
shiftable_usage = []

for x in xrange(period):
	sdate = idate.strftime("%Y-%m-%d")
	print sdate
	data = client.ucap.get_all_vs_shiftable_usage(houseid, sdate)
	
	datum = data['All Traffic']
	date = array_parse_date(datum, 0, timezone)
	usage = array_parse_int(datum, 1)
	is_zero = check_for_zero(usage)
	print usage
	if is_zero:
		idate = idate + one_day
		print '--SKIPPED--\n'
		continue
	all_usage.append(usage)
	
	datum = data['Shiftable Traffic']
	usage = array_parse_int(datum, 1)
	print usage
	shiftable_usage.append(usage)
	
	idate = idate + one_day
	print '\n'
	

# VARDUMP
print 'All Traffic:'
arr_dump(all_usage)
print '\n'

print 'Shiftable Traffic:'
arr_dump(shiftable_usage)
print '\n'

# Calculate the Average
avg_all_traffic = arr_average(all_usage)
avg_shiftable_traffic = arr_average(shiftable_usage)

# Plotting
timeformat = mdates.DateFormatter('%H:%M:%S')
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title(houseid + ' : ' + tdate + ' : ' + str(period))
ax.set_ylabel('Bandwidth Usage (Bytes)')

ax.plot(date, avg_all_traffic, 'o-', label='All Traffic')
ax.plot(date, avg_shiftable_traffic, 'o-', label='Shiftable Traffic')
ax.xaxis.set_major_formatter(timeformat)
fig.autofmt_xdate()
plt.legend(loc='best')

filename = houseid + "_all_vs_shiftable_usage_average.png"
print 'Exporting: ' + filename
plt.savefig(filename)