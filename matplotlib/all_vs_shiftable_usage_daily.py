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
	
########
# MAIN #
########

houseid = ''
idate = ''
try:
	# Get command line args
	houseid = sys.argv[1]
	idate = sys.argv[2]
except:
	print "Usage: " + sys.argv[0] + " house_id date"
	print "Example: " + sys.argv[0] + " OWC43DC7B0AE78 2012-07-14"
	sys.exit(0)
	
# Get data from JSONRPC
client = jsonrpclib.Server('https://localhost/json/json/')
data = client.ucap.get_all_vs_shiftable_usage(houseid, idate)
timezone = get_timezone(houseid)

# Plotting
timeformat = mdates.DateFormatter('%H:%M:%S')
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('All vs Shiftable Usage : ' + houseid + ' : ' + idate)
ax.set_ylabel('Bandwidth Usage (Bytes)')

for key in data:
	datum = data[key]
	date = array_parse_date(datum, 0, timezone)
	usage = array_parse_int(datum, 1)
	ax.plot(date, usage, 'o-', label=key)
	ax.xaxis.set_major_formatter(timeformat)
	
# Rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

# Show legend
plt.legend(loc='best')

# Save to a PNG file
filename = houseid + "_all_vs_shiftable_usage_" + idate + ".png"
print 'Exporting: ' + filename
plt.savefig(filename)



