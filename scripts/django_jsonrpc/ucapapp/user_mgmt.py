#!/usr/bin/env python
import sys
sys.path.append('.')
import pgsql as sql
from gen import *
import time
import datetime

def addHouse(hid,address,details,photofilepath=''):
    unittype = 'household'
    tab = unitTables[unittype]
    name = None
    parentdigest = None
    cmd = "insert into %s (id,address,details) values('%s','%s','%s')"\
      %(tab,hid,address,details)
    res = sql.run_insert_cmd(cmd)
    if res[0] == 1:
      parentdigest = get_digest(hid=hid)
      ctab = unitTables['user']
      cmd = "insert into %s (id,parentdigest,name,details,photo) values('default','%s',"\
        "'Default User','Default for House %s','%s')"%(ctab,parentdigest,hid,photofilepath)
      res1 = sql.run_insert_cmd(cmd)
    return res

def addUser(hid,uid,name,details,photofilepath=''):
    unittype = 'user'
    tab = unitTables[unittype]
    address = None
    parentdigest = get_digest(hid=hid)
    cmd = "insert into %s (id,parentdigest,name,details,photo) values('%s','%s','%s','%s','%s')"\
      %(tab,uid,parentdigest,name,details,photofilepath)
    res = sql.run_insert_cmd(cmd)
    return res

def addDevice(hid,uid,did,name,details,macaddr,photofilepath=''):
    unittype = 'device'
    tab = unitTables[unittype]
    address = None
    if uid == '':
      uid = default_user
    parentdigest = get_digest(hid=hid,uid=uid)
    cmd = "insert into %s (id,parentdigest,name,details,photo,macid) values('%s','%s','%s','%s','%s',"\
      %(tab,did,parentdigest,name,details,photofilepath)
    mcmd = "'{"
    for macid in macaddr:
      mcmd = "%s%s,"%(mcmd,macid)
    mcmd = "%s%s"%(mcmd[0:-1],"}')")
    cmd = "%s%s"%(cmd,mcmd)
    print cmd
    res = sql.run_insert_cmd(cmd)
    return res

def getHouseMetaInfo(hid):
    unittype = 'household'
    tab = unitTables[unittype]
    digest = get_digest(hid=hid)
    cmd = "select id,address,details,photo from %s where digest = '%s'"\
      %(tab,digest)
    print cmd
    res = sql.run_data_cmd(cmd)
    try:
      return (1,(res[0][0],res[0][1],res[0][2],res[0][3]))
    except:
      return (0,('ERROR: No match found'))

def getUserMetaInfo(hid,uid):
    unittype = 'user'
    if uid == '':
      uid = default_user
    tab = unitTables[unittype]
    digest = get_digest(hid=hid,uid=uid)
    cmd = "select id,name,details,photo from %s where digest = '%s'"\
      %(tab,digest)
    res = sql.run_data_cmd(cmd)
    try:
      return (1,(res[0][0],res[0][1],res[0][2],res[0][3]))
    except:
      return (0,('ERROR: No match found'))

def updateHouseMetaInfo(hid,address='',details='',photo=''):
    unittype = 'household'
    tab = unitTables[unittype]
    digest = get_digest(hid=hid)
    cmd = "update %s set "%(tab)
    if address == '' and details == '' and photo == '':
      return (1,("SUCCESS"))
    if address != '':
      cmd = "%s address='%s',"%(cmd,address)
    if details != '':
      cmd = "%s details='%s',"%(cmd,details)
    if photo != '':
      cmd = "%s photo='%s',"%(cmd,photo)
    cmd = "%s where digest = '%s'"%(cmd[:-1],digest)
    print cmd
    res = sql.run_insert_cmd(cmd)
    try:
      return (1,("SUCCESS"))
    except:
      return (0,('ERROR: Could not update table'))

def updateUserMetaInfo(hid,uid,name='',details='',photo='',did=None):
    if did == None:
      unittype = 'User'
      digest = get_digest(hid=hid,uid=uid)
    else:
      unittype = 'Device'
      digest = get_digest(hid=hid,uid=uid,did=did)
    tab = unitTables[unittype]
    cmd = "update %s set "%(tab)
    if name == '' and details == '' and photo == '':
      return (1,("SUCCESS"))
    if name != '':
      cmd = "%s name='%s',"%(cmd,name)
    if details != '':
      cmd = "%s details='%s',"%(cmd,details)
    if photo != '':
      cmd = "%s photo='%s',"%(cmd,photo)
    cmd = "%s where digest = '%s'"%(cmd[:-1],digest)
    print cmd
    res = sql.run_insert_cmd(cmd)
    try:
      return (1,("SUCCESS"))
    except:
      return (0,('ERROR: Could not update table'))
 
def updateDeviceMetaInfo(hid,uid,did,name='',details='',photo=''):
  updateUserMetaInfo(hid,uid,name=name,details=details,photo=photo,did=did)

def getDeviceMetaInfo(hid,uid,did):
    unittype = 'device'
    if uid == '':
      uid = default_user
    tab = unitTables[unittype]
    digest = get_digest(hid=hid,uid=uid,did=did)
    cmd = "select id,name,details,macid,photo from %s where digest = '%s'"\
      %(tab,digest)
    res = sql.run_data_cmd(cmd)
    try:
      return (1,(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4]))
    except:
      return (0,('ERROR: No match found'))

def getHouseInfo(digest):
  unittype = 'household'
  tab = unitTables[unittype]
  cmd = "select id from %s where digest = '%s'"%(tab,digest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0:
      return (0,"ERROR: No match found")
  except:
    return (1,[])
  #if len(res) == 0 or res[0] == 0:
   # return (0,"ERROR: No match found")
  return (1,res[0][0])

def getUserInfo(digest):
  unittype = 'user'
  tab = unitTables[unittype]
  cmd = "select id,parentdigest from %s where digest = '%s'"%(tab,digest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0:
      return (0,"ERROR: No match found")
  except:
    return (1,[])
#if len(res) == 0 or 
  res = res[0]
  return (1,[getHouseInfo(res[1])[1],res[0]])
  
def getDeviceInfo(digest):
  unittype = 'device'
  tab = unitTables[unittype]
  cmd = "select id,parentdigest from %s where digest = '%s'"%(tab,digest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0:
      return (0,"ERROR: No match found")
  except:
    return (1,[])
  #if len(res) == 0 or res[0] == 0:
    #return (0,"ERROR: No match found")
  res = res[0]
  pinfo = getUserInfo(res[1])[1]
  pinfo.append(res[0])
  return (1,pinfo)

def _getChildren(tab,pdigest):
  cmd = "select id from %s where parentdigest = '%s'"\
    %(tab,pdigest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0: 
      return (0,('ERROR: No match found'))
  except:
    return (1,[])
  children = []
  for rec in res:
    children.append(rec[0])
  return (1,children)

def _getChildrenAll(unittype,pdigest):
  if unittype in ['user','device']:
    det = 'u.name,u.details'
  if unittype in ['household']:
    det = 'u.address,u.details'
  utab = unitTables[unittype]
  ctab = capTables[unittype]
  cmd = "select u.id,%s,c.capped,c.cap,c.usage from %s as u,%s as c \
     where u.digest = c.digest and u.parentdigest = '%s'"\
    %(det,utab,ctab,pdigest)
  res = sql.run_data_cmd(cmd,prnt=0)
  try:
    if res[0] == 0: 
      return (0,('ERROR: No match found'))
  except:
    return (1,[])
  children = []
  for rec in res:
    children.append(rec[0:])
  return (1,children)
  
def getHouseUsersDetails(hid):
  unittype = 'user'
  digest = get_digest(hid=hid)
  return _getChildrenAll(unittype,digest)

def getUserDevicesDetails(hid,uid):
  unittype = 'device'
  if uid == '':
    uid = default_user
  digest = get_digest(hid=hid,uid=uid)
  return _getChildrenAll(unittype,digest)

def getHouseUsers(hid):
    unittype = 'user'
    tab = unitTables[unittype]
    digest = get_digest(hid=hid)
    return _getChildren(tab,digest)

def getUserDevices(hid,uid):
    unittype = 'device'
    tab = unitTables[unittype]
    if uid == '':
      uid = default_user
    digest = get_digest(hid=hid,uid=uid)
    return _getChildren(tab,digest)

def getHouseDevices(hid):
  urec = getHouseUsers(hid)
  if urec[0] == 0:
    return (0,"ERROR: No users for house")
  users = urec[1]
  devices = []
  for user in users:
    drec = getUserDevices(hid,user) 
    if drec[0] == 1:
      devices.extend(drec[1])
  return (1,devices)

def getDeviceMacs(hid,uid,devices):
  macs = []
  unittype = 'device'
  tab = unitTables[unittype]
  if uid == '':
    uid = default_user
  for did in devices:
    digest = get_digest(hid=hid,uid=uid,did=did)
    cmd = "select id,macid from %s where digest = '%s'"%(tab,digest)
    res = sql.run_data_cmd(cmd)
    print cmd,res
    try:
      if res[0] == 0:
        return (0,'ERROR')
    except:
      if len(res) == 0:
        return (1,[])
    rec = res[0]
    tmac = rec[1].replace('{','').replace('}','').split(',')
    macs.extend(tmac) 
  return (1,macs)
  
def getUserDeviceMacs(hid,uid):
  res = getUserDevices(hid,uid)
  if res[0] == 0:
    return res
  return getDeviceMacs(hid,uid,res[1])

def getHouseDeviceMacs(hid):
  res = getHouseUsers(hid)
  if res[0] == 0:
    return res
  macs = []
  for user in res[1]:
    res = getUserDeviceMacs(hid,user)
    if res[0] == 1:
      macs.extend(res[1])
  #if len(macs) == 0: 
  #  return (0,"ERROR: No match found")
  return (1,macs)
  

def moveDevice(hid,ouid,nuid,did):
    unittype = 'device'
    utab = unitTables[unittype]
    ctab = capTables[unittype]
    if ouid == '':
      ouid = default_user
    if nuid == '':
      nuid = default_user
    if nuid == ouid:
      return(1,"SUCCESS")
    odigest = get_digest(hid,ouid,did)
    ndigest = get_digest(hid,nuid,did)
    npdigest = get_digest(hid,nuid)
    #cmd1 = "update %s set parentdigest = '%s' where capped is True and cap != 'Infinity' and digest = '%s'"%(ctab,npdigest,odigest)
    cmd1 = "update %s set parentdigest = '%s' where digest = '%s'"%(utab,npdigest,odigest)
    cmd2 = "update %s set digest = '%s' where digest = '%s'"%(utab,ndigest,odigest)
    prnt = 1 
    conn = sql.sqlconn()
    sql.run_insert_cmd("begin",conn=conn,prnt=prnt)
    for cmd in [cmd1,cmd2]:
      res = sql.run_insert_cmd(cmd,conn=conn,prnt=prnt)
      if res[0] == 0:
        sql.run_insert_cmd("rollback",conn=conn,prnt=prnt)
        return (0,"ERROR")
    sql.run_insert_cmd("commit",conn=conn,prnt=prnt)
    return (1,"SUCCESS")

def getDeviceUsageOnDay(macs,date,timezone):
    gmacs = get_group(macs,"'")
    arr_date = date.split('-')
    sdate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 0, 0, 0)
    edate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 23, 59, 59)
    delta = datetime.timedelta(hours=timezone)
    
    sdate = sdate - delta
    edate = edate - delta
    start = sdate.strftime("%Y-%m-%d %H:%M:%S+00")
    end = edate.strftime("%Y-%m-%d %H:%M:%S+00")
    
    cmd = "select devices.name, t.timestamp as d, t.bytes from bismark_passive.bytes_per_device_per_hour as t,devices where t.mac_address in %s and devices.macid[1]=t.mac_address and t.timestamp between '%s' and '%s' order by t.mac_address,d asc"%(gmacs,start,end)
    #cmd = "select t.mac_address, t.timestamp as d, t.bytes from bismark_passive.bytes_per_device_per_hour as t where t.mac_address in %s and t.timestamp between '%s' and '%s' order by t.mac_address,d asc"%(gmacs, start, end)
    res = sql.run_data_cmd(cmd)
    
    out = {}
    # Deal with data from database first
    for rec in res:
        try:
            out[rec[0]].append((rec[1][0:len(rec[1]) - 3],rec[2]))
        except:
            out[rec[0]] = []
            out[rec[0]].append((rec[1][0:len(rec[1]) - 3],rec[2]))

    # Fill in 0s for missing hours (where usage is actually 0)
    one_hour = datetime.timedelta(hours=1)
    for dev in out:
        idate = datetime.datetime(*(time.strptime(start, "%Y-%m-%d %H:%M:%S+00")[0:6]))
        index = 0
        for x in xrange(24):
            sdate = idate.strftime("%Y-%m-%d %H:%M:%S")
            try:
                tdate = datetime.datetime(*(time.strptime(out[dev][index][0], "%Y-%m-%d %H:%M:%S")[0:6]))
                if idate.hour == tdate.hour:
                    index = index + 1
                else:
                    out[dev].append((sdate,0))
            except:
                out[dev].append((sdate,0))
            idate = idate + one_hour
        out[dev] = sorted(out[dev], key=lambda dates: dates[0])
    
    return out

def getDomainUsageOnDay(nodeid,topn,date,timezone):    
    arr_date = date.split('-')
    sdate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 0, 0, 0)
    edate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 23, 59, 59)
    delta = datetime.timedelta(hours=timezone)
    
    sdate = sdate - delta
    edate = edate - delta
    start = sdate.strftime("%Y-%m-%d %H:%M:%S+00")
    end = edate.strftime("%Y-%m-%d %H:%M:%S+00")
    
    cmd = "select t.timestamp as d, t.domain, t.bytes as s from bismark_passive.bytes_per_domain_per_hour as t where t.node_id='%s' and t.timestamp between '%s' and '%s' order by d asc,s desc"%(nodeid,start,end)
    res = sql.run_data_cmd(cmd)
    
    out = {}
    # Deal with data from database first
    for rec in res:
        date = rec[0][0:len(rec[0]) - 3]
        try:
            if topn < 0 or len(out[date]) < topn :
                out[date].append((rec[1],rec[2]))
        except:
            out[date] = []
            out[date].append((rec[1],rec[2]))

    return out

def getBytesOnDay(nodeid,date,timezone):
    arr_date = date.split('-')
    sdate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 0, 0, 0)
    edate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 23, 59, 59)
    delta = datetime.timedelta(hours=timezone)
    
    sdate = sdate - delta
    edate = edate - delta
    start = sdate.strftime("%Y-%m-%d %H:%M:%S+00")
    end = edate.strftime("%Y-%m-%d %H:%M:%S+00")
    
    cmd = "select t.timestamp as d, t.bytes as s from bismark_passive.bytes_per_hour as t where t.node_id='%s' and t.timestamp between '%s' and '%s' order by d asc"%(nodeid,start,end)
    res = sql.run_data_cmd(cmd)
    
    out = []
    # Deal with data from database first
    for rec in res:
        try:
            out.append((rec[0][0:len(rec[0]) - 3],rec[1]))
        except:
            out = []
            out.append((rec[0][0:len(rec[0]) - 3],rec[1]))
    
    # Fill in 0s for missing hours (where usage is actually 0)
    one_hour = datetime.timedelta(hours=1)
    idate = datetime.datetime(*(time.strptime(start, "%Y-%m-%d %H:%M:%S+00")[0:6]))
    index = 0
    for x in xrange(24):
        sdate = idate.strftime("%Y-%m-%d %H:%M:%S")
        try:
            tdate = datetime.datetime(*(time.strptime(out[index][0], "%Y-%m-%d %H:%M:%S")[0:6]))
            if idate.hour == tdate.hour:
                index = index + 1
            else:
                out.append((sdate,0))
        except:
            out.append((sdate,0))
        idate = idate + one_hour
    out = sorted(out, key=lambda dates: dates[0])
    
    return out

def getAllBytesOnDay(date,timezone):
    # Get all node_id
    cmd = "select distinct t.node_id from bismark_passive.bytes_per_hour as t"
    res = sql.run_data_cmd(cmd)
    
    # Get byte usage for each node_id
    out = {}
    for rec in res:
        out[rec[0]] = []
        total = 0;
        bytes = getBytesOnDay(rec[0], date, timezone)
        for byte in bytes:
            total += byte[1]
            out[rec[0]].append(byte)
        if total == 0:
            del out[rec[0]]

    return out

def getDeviceUsageInterval(macs,start,end,timezone):
	delta = datetime.timedelta(hours=timezone)
	arr_sdate = start.split('-')
	sdate = datetime.datetime(int(arr_sdate[0]), int(arr_sdate[1]), int(arr_sdate[2]), 0, 0, 0)
	sdate = sdate - delta
	start = sdate.strftime("%Y-%m-%d %H:%M:%S+00")
	
	arr_edate = end.split('-')
	edate = datetime.datetime(int(arr_edate[0]), int(arr_edate[1]), int(arr_edate[2]), 0, 0, 0)
	edate = edate - delta
	end = edate.strftime("%Y-%m-%d %H:%M:%S+00")
	
	gmacs = get_group(macs,"'")
	cmd = "select devices.name, date(t.timestamp) as d, sum(t.bytes) from bismark_passive.bytes_per_device_per_hour as t,devices where t.mac_address in %s and devices.macid[1]=t.mac_address and t.timestamp between '%s' and '%s' group by devices.name,t.mac_address,d order by t.mac_address,d asc"%(gmacs,start,end)
	#  cmd = "select t.mac_address, date(t.timestamp) as d, sum(t.bytes) from bismark_passive.bytes_per_device_per_hour as t where t.mac_address in %s and t.timestamp between '%s' and '%s' group by t.mac_address,d order by t.mac_address,d asc"%(gmacs,start,end)
	res = sql.run_data_cmd(cmd)
	out = {}
	thedate = ''
	value = 0
	sd = datetime.datetime(int(arr_sdate[0]), int(arr_sdate[1]), int(arr_sdate[2]))
	ed = datetime.datetime(int(arr_edate[0]), int(arr_edate[1]), int(arr_edate[2]))
	
	# Deal with data from database first
	for rec in res:
		try:
			out[rec[0]].append((rec[1],rec[2]))
		except:
			out[rec[0]] = []
			out[rec[0]].append((rec[1],rec[2]))
	
	# Fill in 0s for missing dates (where usage is actually 0).
	for dev in out:
		for n in range((ed-sd).days+1):
			found = False
			curr_date_d = sd+datetime.timedelta(n)
			curr_date = (curr_date_d).timetuple()
			for entry in out[dev]:
				entry_date = time.strptime(entry[0],'%Y-%m-%d')
				if curr_date == entry_date:
					found = True
					break
			if found is False:
				scurr_date_d = curr_date_d.strftime("%Y-%m-%d")
				out[dev].append((scurr_date_d,0))
		out[dev] = sorted(out[dev], key=lambda dates: dates[0])
	
	return out
	
def getDomainUsageInterval(nodeid,topn,start,end,timezone):
	delta = datetime.timedelta(hours=timezone)
	arr_sdate = start.split('-')
	sdate = datetime.datetime(int(arr_sdate[0]), int(arr_sdate[1]), int(arr_sdate[2]), 0, 0, 0)
	sdate = sdate - delta
	start = sdate.strftime("%Y-%m-%d %H:%M:%S+00")
	
	arr_edate = end.split('-')
	edate = datetime.datetime(int(arr_edate[0]), int(arr_edate[1]), int(arr_edate[2]), 0, 0, 0)
	edate = edate - delta
	end = edate.strftime("%Y-%m-%d %H:%M:%S+00")
	
	cmd = "select t.domain, sum(t.bytes) as s from bismark_passive.bytes_per_domain_per_hour as t where node_id = '%s' and t.timestamp between '%s' and '%s' group by t.domain order by s desc"%(nodeid,start,end)
	res = sql.run_data_cmd(cmd)
	doms = []
	tot = 0
	for rec in res:
		tot += int(rec[1])
		if rec[0] is not None:
			doms.append((rec[0],rec[1]))
	tdoms = doms[:topn]
	
	#  print tot
	out = {"other":[]}
	otot = 0
	for domd in tdoms:
		try:
			out[domd[0]].append((domd[1],float(domd[1])/tot))
			otot += domd[1]
		except:
			out[domd[0]] = []
			out[domd[0]].append((domd[1],float(domd[1])/tot))
			otot += domd[1]
	out["other"].append((tot-otot,(tot-otot)/tot)) 
	
	return out 

def getPeakHoursUsage(hid,milestone,start,end):
    return 100

def getShiftableUsage(nodeid,date,timezone):
    #Shiftable domains
    shiftable = ['akamai.net',
                 'amazonaws.com',
                 'llnwd.net']
    
    res = getDomainUsageOnDay(nodeid,-1,date,timezone)
    
    out = {}
    out['shiftable'] = []
    out['nonshiftable'] = []
    
    arr_date = date.split('-')
    idate = datetime.datetime(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]), 0, 0, 0)
    delta = datetime.timedelta(hours=timezone)
    idate = idate - delta
    one_hour = datetime.timedelta(hours=1)
    for x in xrange(24):
        sdate = idate.strftime("%Y-%m-%d %H:%M:%S")
        rec = res[sdate]
        
        shiftable_usage = 0
        non_shiftable_usage = 0
        for entry in rec:
            domain = entry[0]
            if domain in shiftable:
                shiftable_usage += entry[1]
            else:
                non_shiftable_usage += entry[1]

        out['shiftable'].append([sdate, shiftable_usage])
        out['nonshiftable'].append([sdate, non_shiftable_usage])
        idate = idate + one_hour
    return out
