# Create your views here.
import sys
sys.path.append('.')

from netaddr import *
import pgsql as sql
from gen import *
import user_mgmt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from jsonrpc import jsonrpc_method
import imgform
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import StringIO
import Image


SECURITY_BEEF = False

@jsonrpc_method('ucap.update_house_startdate')
def update_house_startdate_dj(request,hid,startdate):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return update_house_startdate(hid,startdate)

@jsonrpc_method('ucap.image_upload_user')
def image_upload_user_dj(request,email):
    if SECURITY_BEEF is True and check_auth_and_uid(request,email) is False:
        print 'Not right user. not allowed.'
        return

    # Get hid
    hid = getHouseInfo(getHouseDigestFromUserID(email))
    hid = hid[1]

    return image_upload(request,hid,email)

@jsonrpc_method('ucap.image_upload_device')
def image_upload_device_dj(request,email,did):
    if SECURITY_BEEF is True and check_auth_and_uid(request,email) is False:
        print 'Not right user. not allowed.'
        return            

    # Get hid
    hid = getHouseInfo(getHouseDigestFromUserID(email))
    hid = hid[1]

    return image_upload(request,hid,email,did)

@jsonrpc_method('ucap.is_authed')
def check_authed(request):
    if request.user.is_authenticated():
        return '1'
    else:
        return '0'

@jsonrpc_method('ucap.user_logout')
def user_logout(request):
    logout(request)

@jsonrpc_method('ucap.user_login')
def user_login(request,ent_username,ent_password):
    user = authenticate(username=ent_username,password=ent_password)
    hid = getHouseInfo(getHouseDigestFromUserID(ent_username))
    hid = hid[1]
    res = []

    if user is not None:
        if user.is_active:
            if not request.user.is_authenticated():
                login(request,user)
                res = [0,'LOGIN SUCCESS',hid]
            else:
                res = [0,'ALREADY LOGGED IN',hid]
        else:
            res = [-1,'USER NOT ACTIVE',hid]
    else:
        res = [-1,'NO MATCHING ENTRY',hid]

    return res

@jsonrpc_method('ucap.delUser')
def delUser(request,hid,ent_username):
    if check_localhost(request) is False:
        print 'Not localhost, not allowed.'
        return            

    user = User.objects.get(username__exact=ent_username)
#    hid = getHouseInfo(getHouseDigestFromUserID(ent_username))
#    hid = hid[1]
    res = []

    # uCap DB
    digest = get_digest(hid=hid,uid=ent_username)
    cmd = "DELETE FROM users where digest='%s'"%(digest)
    res_2 = sql.run_insert_cmd(cmd)
    if res_2[0]==0:
        print 'Failed to remove'
        return res_2

    # Auth DB
    if user is not None:
        if user.is_active:
            user.delete()
            res = [0,'Deleted',hid]
        else:
            res = [-1,'USER NOT ACTIVE',hid]
    else:
        res = [-1,'NO MATCHING ENTRY',hid]

    return res 

@jsonrpc_method('ucap.check_uid_existence')
def check_uid_existence_dj(request,hid,uid):
    if check_localhost(request) is False:
        print 'Not localhost, not allowed.'
        return

    retval = []
    exist = check_uid_existence(hid,uid)
    if exist is True:
        retval = [1,'t']
    else:
        retval = [1,'f']
    return retval

@jsonrpc_method('ucap.check_hid_existence')
def check_hid_existence_dj(request,hid):
    if check_localhost(request) is False:
        print 'Not localhost, not allowed.'
        return

    retval = []
    exist = check_hid_existence(hid)
    if exist is True:
        retval = [1,'t']
    else:
        retval = [1,'f']
    return retval

@jsonrpc_method('ucap.change_password')
def changePasswd_dj(request, email,passwd,new_passwd):
    if SECURITY_BEEF is True and check_auth_and_uid(request,email) is False:
        print 'Not right user. not allowed.'
        return            

    return changePasswd(email,passwd,new_passwd)

@jsonrpc_method('ucap.lost_password')
def lost_password_dj(request,email):
    return lost_password(email)

@jsonrpc_method('ucap.addHouse')
def addHouse_dj(request, hid,address,details,photofilepath):
    if check_localhost(request) is False:
        print 'Not localhost, not allowed.'
        return            

    return addHouse(hid,address,details,photofilepath)

@jsonrpc_method('ucap.addUser')
def addUser_dj(request, hid,uid,name,details,email,passwd,role,notify,notifyperc,notified,photofilepath):
    if check_localhost(request) is False:
        print 'Not localhost, not allowed.'
        return            

    return addUser_new(hid,uid,name,details,email,passwd,role,notify,notifyperc,notified,photofilepath)

@jsonrpc_method('ucap.addDevice')
def addDevice_dj(request, hid,uid,did,name,details,macaddr,photofilepath):
    if check_localhost(request) is False:
        print 'Not localhost, not allowed.'
        return            

    return addDevice(hid,uid,did,name,details,macaddr,photofilepath)

@jsonrpc_method('ucap.getHouseMetaInfo')
def getHouseMetaInfo_dj(request, hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getHouseMetaInfo(hid)

@jsonrpc_method('ucap.getUserMetaInfo')
def getUserMetaInfo_dj(request, hid,uid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getUserMetaInfo_new(hid,uid)

@jsonrpc_method('ucap.getDeviceMetaInfo')
def getDeviceMetaInfo_dj(request, hid,uid,did):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getDeviceMetaInfo(hid,uid,did)

@jsonrpc_method('ucap.getDeviceMetaInfo_ex')
def getDeviceMetaInfo_ex_dj(request, hid,uid,did):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getDeviceMetaInfo_ex(hid,uid,did)

@jsonrpc_method('ucap.DeviceUsagebymac')
def DeviceUsagebymac_dj(request, action,what,macaddr,val=None):
    return DeviceUsagebymac(action,what,macaddr,val)

@jsonrpc_method('ucap.getHouseInfo')
def getHouseInfo_dj(request, digest):
    return getHouseInfo(digest)

@jsonrpc_method('ucap.getUserInfo')
def getUserInfo_dj(request, digest):
    return getUserInfo(digest)

@jsonrpc_method('ucap.getDeviceInfo')
def getDeviceInfo_dj(request, digest):
    return getDeviceInfo(digest)

@jsonrpc_method('ucap.getHouseUsersDetails')
def getHouseUsersDetails_dj(request, hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getHouseUsersDetails(hid)

@jsonrpc_method('ucap.getUserDevicesDetails')
def getUserDevicesDetails_dj(request, hid, uid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getUserDevicesDetails(hid,uid)

@jsonrpc_method('ucap.getHouseUsers')
def getHouseUsers_dj(request, hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getHouseUsers(hid)

@jsonrpc_method('ucap.getUserDevices')
def getUserDevices_dj(request, hid,uid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getUserDevices(hid,uid)
 
@jsonrpc_method('ucap.getHouseDevices')
def getHouseDevices_dj(request, hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getHouseDevices(hid)

@jsonrpc_method('ucap.getDeviceMacs')
def getDeviceMacs_dj(request, hid,uid,devices):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getDeviceMacs(hid,uid,devices)

@jsonrpc_method('ucap.getUserDeviceMacs')
def getUserDeviceMacs_dj(request, hid,uid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getUserDeviceMacs(hid,uid)

@jsonrpc_method('ucap.getHouseDeviceMacs')
def getHouseDeviceMacs_dj(request, hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getHouseDeviceMacs(hid)

@jsonrpc_method('ucap.moveDevice')
def moveDevice_dj(request, hid,ouid,nuid,did):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return moveDevice(hid,ouid,nuid,did)

@jsonrpc_method('ucap.getHouseCapUsageInfo')
def getHouseCapUsageInfo_dj(request, hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return getHouseCapUsageInfo(hid)

@jsonrpc_method('ucap.HouseUsage')
def HouseUsage_dj(request, action,what,hid,val=None):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return HouseUsage(action,what,hid,val)

@jsonrpc_method('ucap.UserUsage')
def UserUsage_dj(request, action,what,hid,uid,val=None):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return UserUsage(action,what,hid,uid,val)

@jsonrpc_method('ucap.DeviceUsage')
def DeviceUsage_dj(request, action,what,hid,uid,did,val=None):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return DeviceUsage(action,what,hid,uid,did,val)

@jsonrpc_method('ucap.getHouseDisable')
def getHouseDisable_dj(request):
    return getHouseDisable()

@jsonrpc_method('ucap.getUserDisable')
def getUserDisable_dj(request):
    return getUserDisable()

@jsonrpc_method('ucap.getDeviceDisable')
def getDeviceDisable_dj(request):
    return getDeviceDisable()

@jsonrpc_method('ucap.getHouseEnable')
def getHouseEnable_dj(request):
    return getHouseEnable()

@jsonrpc_method('ucap.getUserEnable')
def getUserEnable_dj(request):
    return getUserEnable()

@jsonrpc_method('ucap.getDeviceEnable')
def getDeviceEnable_dj(request):
    return getDeviceEnable()

@jsonrpc_method('ucap.UserCapExchange')
def UserCapExchange_dj(request, hid,fuid,tuid,val):
    return UserCapExchange(hid,fuid,tuid,val)

@jsonrpc_method('ucap.updateHouseMetaInfo')
def updateHouseMetaInfo_dj(request,hid,address,details,photo=None):
    if photo==None:
        photo=''
    return updateHouseMetaInfo(hid,address,details,photo)

@jsonrpc_method('ucap.updateUserMetaInfo')
#def updateUserMetaInfo_dj(request,hid,uid,name,details,notify,notifyperc,notified,role,contact,passwd,photo=None):
def updateUserMetaInfo_dj(request,hid,uid,name,details,notify,notifyperc,notified,photo,role,contact):
    return updateUserMetaInfo_new(hid,uid,name,details,notify,notifyperc,notified,photo,role,contact)
#return updateUserMetaInfo_new(hid,uid,name,details,notify,notifyperc,notified,photo,role,contact,passwd)

@jsonrpc_method('ucap.updateDeviceMetaInfo_ex')
def updateDeviceMetaInfo_ex_dj(request,hid,uid,did,name,details,notify,notifyperc,notified,photo=None):
    if photo==None:
        photo=''
    return updateDeviceMetaInfo_new(hid,uid,did,name,details,notify,notifyperc,notified,photo)

@jsonrpc_method('ucap.updateDeviceMetaInfo')
def updateDeviceMetaInfo_dj(request,hid,uid,did,name,details,photo=None):
    if photo==None:
        photo=''
    return updateDeviceMetaInfo(hid,uid,did,name,details,photo)

@jsonrpc_method('ucap.deviceNameBymac')
def deviceNameBymac_dj(request,macaddr):
    utype = 'device'
    tab = capTables[utype]
    utab = unitTables[utype]
    cmd = "select name from %s where '%s' = any(macid)"\
      %(utab,macaddr)
    res = sql.run_data_cmd(cmd)
    name = ''
    try:
  	name = res[0][0]
        return name
    except:
        return [0,'ERROR: No Match']

@jsonrpc_method('ucap.logging_calls')
def loggingCalls_dj(request,hid,method,params,date):
    return loggingCalls(hid,method,params,date)

@jsonrpc_method('ucap.user_logs')
def user_logs_dj(request,hid):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return user_logs(hid);

@jsonrpc_method('ucap.user_logs_ex')
def user_logs_ex_dj(request,hid,start,end):
    if SECURITY_BEEF is True and check_auth_and_hid(request,hid) is False:
        print 'Not right user for household.'
        return

    return user_logs_ex(hid,start,end)

@jsonrpc_method('ucap.get_device_usage_on_day')
def get_device_usage_on_day_dj(request,macs,date,timezone):
    return user_mgmt.getDeviceUsageOnDay(macs,date,timezone)

@jsonrpc_method('ucap.get_device_domain_on_day')
def get_device_domain_on_day_dj(request,nodeid,topn,date,timezone):
    return user_mgmt.getDomainUsageOnDay(nodeid,topn,date,timezone)

@jsonrpc_method('ucap.get_bytes_on_day')
def get_bytes_on_day_dj(request,nodeid,date,timezone):
    return user_mgmt.getBytesOnDay(nodeid,date,timezone)

@jsonrpc_method('ucap.get_all_bytes_on_day')
def get_all_bytes_on_day_dj(request,date,timezone):
    return user_mgmt.getAllBytesOnDay(date,timezone)

@jsonrpc_method('ucap.get_device_usage_interval')
def get_device_usage_interval_dj(request,macs,start,end):
    return user_mgmt.getDeviceUsageInterval(macs,start,end)

@jsonrpc_method('ucap.get_device_domain_interval')
def get_device_domain_interval_dj(request,nodeid,topn,start,end):
    return user_mgmt.getDomainUsageInterval(nodeid,topn,start,end)

@jsonrpc_method('ucap.get_oui')
def get_oui_dj(request,oui_addr):
    return getOUI(oui_addr)

#######

def check_uid_existence(hid,uid):
    unittype = 'user'
    tab = unitTables[unittype]
    digest = get_digest(hid=hid,uid=uid)

    cmd = "select id from %s where digest = '%s'"%(tab,digest)
    res = sql.run_data_cmd(cmd)
    if not res:
        return False
    else:
        return True
 
def check_hid_existence(hid):
    unittype = 'household'
    tab = unitTables[unittype]
    digest = get_digest(hid=hid)

    cmd = "select id from %s where digest = '%s'"%(tab,digest)
    res = sql.run_data_cmd(cmd)
    if not res:
        return False
    else:
        return True
   
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
#      cmd = "insert into %s (id,parentdigest,name,details,photo) values('default','%s',"\
#        "'Default User','Default for House %s','%s')"%(ctab,parentdigest,hid,photofilepath)
      cmd = "insert into %s (id,parentdigest,name,details,photo) values('default','%s',"\
        "'Default User','Default for House %s','%s')"%(ctab,parentdigest,hid,photofilepath)

      res1 = sql.run_insert_cmd(cmd)
    return [res]

def addUser(hid,uid,name,details,photofilepath=''):
    unittype = 'user'
    tab = unitTables[unittype]
    address = None
    parentdigest = get_digest(hid=hid)
    cmd = "insert into %s (id,parentdigest,name,details,photo) values('%s','%s','%s','%s','%s')"\
      %(tab,uid,parentdigest,name,details,photofilepath)
    res = sql.run_insert_cmd(cmd)
    return [res]

def addUser_new(hid,uid,name,details,email,passwd,role,notify,notifyperc,notified,photofilepath=''):
    unittype = 'user'
    tab = unitTables[unittype]
    address = None
    role_this = role
    parentdigest = get_digest(hid=hid)
    if (role=='admin' or role=='user'): # if real user, add to user auth table
        user = User.objects.create_user(uid,email,passwd)
        if user is not None:
            user.save()
        else:
            return -1
    else:
         if (role!='ghost'):
            print 'Wrong role argument.'
            return ['Wrong role parameter. Should be admin,user or ghost']
    cmd = "insert into %s (id,parentdigest,name,details,photo,contact,role,notify,notifyperc,notified) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"\
      %(tab,uid,parentdigest,name,details,photofilepath,email,role_this,notify,notifyperc,notified)
    res = sql.run_insert_cmd(cmd)
    if (role=='admin'):
        cmd1 = "update %s set contact = '%s' where parentdigest = '%s' and id = 'default'"%(tab,email,parentdigest)
        res2 = sql.run_insert_cmd(cmd1)
    return [res]

def changePasswd(email,passwd,new_passwd):
    user = authenticate(username=email,password=passwd)
    res = []
    if user is not None:
        user.set_password(new_passwd)
        user.save()
        res = [0,'CHANGE SUCCESS']
    else:
        res = [-1,'CHANGE FAILED. USER INPUT NOT MATCHING.']
    return res

def lost_password(email):
    res = []
    user = User.objects.get(username__exact=email)
    if user is not None:
        rand_passwd = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        
        subject = '[ucap] User password recovery request'
        message = 'You have requested a recovery a lost password for user %s. \n\n'%(email)+ \
                   '========\nNew password is: %s\n========\n\n'%(rand_passwd)+ \
                   'Please consider changing this temporary password to the one you can remember better.\n\n'+ \
                   'Thank you,\nProject uCap team\n'
        ress = user.email_user(subject, message, from_email='ucap-admin@mail.noise.gatech.edu')
        user.set_password(rand_passwd)
        user.save()

        res = [0,'EMAIL SENT WITH NEW PASSWORD']
    else:
        res = [-1,'NO EMAIL ADDRESS MATCHING']

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
    res = sql.run_insert_cmd(cmd)
    return [res]

def getHouseMetaInfo(hid):
    unittype = 'household'
    tab = unitTables[unittype]
    utab = capTables[unittype]
    digest = get_digest(hid=hid)
    cmd = "select h.id,h.address,h.details,h.photo,u.cap,u.usage,u.capped,u.startdt from %s as h, %s as u \
           where h.digest = '%s' and u.digest = '%s'"%(tab,utab,digest,digest)
    res = sql.run_data_cmd(cmd)
    tmp = []
    tmp = list(res[0])
    inf_idx = 4
    if res[0][inf_idx]==float('inf'):
        tmp[inf_idx] = float(-1)
    try:
        return [1,(tmp[0],tmp[1],tmp[2],tmp[3],tmp[4],tmp[5],tmp[6],tmp[7])]
#        return [1,(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4],res[0][5],res[0][6],res[0][7])]
    except:
        return [0,('ERROR: No match found')]

def getHouseCapUsageInfo(hid):
    unittype = 'household'
#    tab = unitTables[unittype]
    tab = capTables[unittype]
    digest = get_digest(hid=hid)
    cmd = "select capped,cap,usage from %s where digest = '%s'"\
      %(tab,digest)
#    print cmd
    res = sql.run_data_cmd(cmd)
    try:
      return [1,(res[0][0],res[0][1],res[0][2])]
    except:
      return [0,('ERROR: No match found')]

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
      return [1,(res[0][0],res[0][1],res[0][2],res[0][3])]
    except:
      return [0,('ERROR: No match found')]

def getUserMetaInfo_new(hid,uid):
    unittype = 'user'
    if uid == '':
      uid = default_user
    tab = unitTables[unittype]
    digest = get_digest(hid=hid,uid=uid)
    cmd = "select id,name,details,notify,notifyperc,notified,photo,role,contact from %s where digest = '%s'"\
      %(tab,digest)
    res = sql.run_data_cmd(cmd)
    try:
      return [1,(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4],res[0][5],res[0][6],res[0][7],res[0][8])]
    except:
      return [0,('ERROR: No match found')]

def getDeviceMetaInfo_ex(hid,uid,did):
    unittype = 'device'
    if uid == '':
      uid = default_user
    tab = unitTables[unittype]
    digest = get_digest(hid=hid,uid=uid,did=did)
    cmd = "select id,name,details,macid,photo,notify,notifyperc,notified from %s where digest = '%s'"\
      %(tab,digest)
    res = sql.run_data_cmd(cmd)
    try:
      return [1,(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4],res[0][5],res[0][6],res[0][7])]
    except:
      return [0,('ERROR: No match found')]


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
      return [1,(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4])]
    except:
      return [0,('ERROR: No match found')]

def getHouseInfo(digest):
  unittype = 'household'
  tab = unitTables[unittype]
  cmd = "select id from %s where digest = '%s'"%(tab,digest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0:
        return [0,"ERROR: No match found"]
  except:
    return [1,[]]
  #if len(res) == 0 or res[0] == 0:
   # return (0,"ERROR: No match found")
  return [1,res[0][0]]

def getUserInfo(digest):
  unittype = 'user'
  tab = unitTables[unittype]
  cmd = "select id,parentdigest from %s where digest = '%s'"%(tab,digest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0:
       return [0,"ERROR: No match found"]
  except:
    return [1,[]]
#if len(res) == 0 or 
  res = res[0]
  return [1,[getHouseInfo(res[1])[1],res[0]]]
  
def getDeviceInfo(digest):
  unittype = 'device'
  tab = unitTables[unittype]
  cmd = "select id,parentdigest from %s where digest = '%s'"%(tab,digest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0:
      return [0,"ERROR: No match found"]
  except:
    return [1,[]]
  #if len(res) == 0 or res[0] == 0:
    #return (0,"ERROR: No match found")
  res = res[0]
  pinfo = getUserInfo(res[1])
  pinfo.append(res[0])
  return [1,pinfo]

def _getChildren(tab,pdigest):
  cmd = "select id from %s where parentdigest = '%s'"\
    %(tab,pdigest)
  res = sql.run_data_cmd(cmd)
  try:
    if res[0] == 0: 
      return [0,('ERROR: No match found')]
  except:
    return [1,[]]
  children = []
  for rec in res:
    children.append(rec[0])
  return [1,children]

def _getChildrenAll(unittype,pdigest,hid=None):
  inf_idx = 0
  if unittype in ['device']:
    det = 'u.name,u.details,u.photo'
    inf_idx = 5
  if unittype in ['user']:
    det = 'u.name,u.details,u.notify,u.notifyperc,u.notified,u.photo,u.role,u.contact'
    inf_idx = 10
#det = 'u.name,u.details'
  if unittype in ['household']:
    det = 'u.address,u.details'
    inf_idx = 4
  utab = unitTables[unittype]
  ctab = capTables[unittype]

  if unittype in ['device']:
#    cmd = "select u.id,%s,c.capped,c.cap,c.usage from %s as u,%s as c \
#       where u.digest = c.digest and u.parentdigest = '%s'"\
#      %(det,utab,ctab,pdigest)
    cmd = "select u.id,%s,c.capped,c.cap,c.usage,u.notify,u.notifyperc,u.notified from %s as u,%s as c,bismark_passive.bytes_per_device_per_hour as t \
       where u.digest = c.digest and u.parentdigest = '%s' and CAST (u.id AS macaddr) = t.mac_address \
       group by u.id,u.name,u.details,u.photo,c.capped,c.cap,c.usage,u.notify,u.notifyperc,u.notified having sum(t.bytes) > %s"\
       %(det,utab,ctab,pdigest,10000)
  else:
    cmd = "select u.id,%s,c.capped,c.cap,c.usage from %s as u,%s as c \
       where u.digest = c.digest and u.parentdigest = '%s'"\
      %(det,utab,ctab,pdigest)
  res = sql.run_data_cmd(cmd,prnt=0)
  try:
    if res[0] == 0: 
      return [0,('ERROR: No match found')]
  except:
    return [1,[]]
  children = []
  for rec in res:
    tmp = []
    tmp = list(rec)
    if rec[inf_idx]==float('inf'):
      tmp[inf_idx] = float(-1)
    if unittype in ['device']:
      macaddr = str(rec[0])
      macaddr = macaddr.lower()
#      if not macaddr.startswith('ffffff') and not macaddr.startswith('3333') and not macaddr.startswith('01005e') and not macaddr.startswith('c43dc7'):
      if not macaddr.startswith('ffffff') and not macaddr.startswith('3333') and not macaddr.startswith('01005e'):
        children.append(tmp[0:])
    else:
      children.append(tmp[0:])
  return [1,children]
  
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
    return [0,"ERROR: No users for house"]
  users = urec[1]
  devices = []
  for user in users:
    drec = getUserDevices(hid,user) 
    if drec[0] == 1:
      devices.extend(drec[1])
  return [1,devices]

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
    try:
      if res[0] == 0:
        return [0,'ERROR']
    except:
      if len(res) == 0:
        return [1,[]]
    rec = res[0]
    tmac = rec[1].replace('{','').replace('}','').split(',')
    macs.extend(tmac) 
  return [1,macs]
  
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
  return [1,macs]
  

def moveDevice(hid,ouid,nuid,did):
    unittype = 'device'
    utab = unitTables[unittype]
    ctab = capTables[unittype]
    if ouid == '':
      ouid = default_user
    if nuid == '':
      nuid = default_user
    if nuid == ouid:
      return [1,"SUCCESS"]
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
        return [0,"ERROR"]
    sql.run_insert_cmd("commit",conn=conn,prnt=prnt)
    return [1,"SUCCESS"]
############

def _updateUnit(utype,action,what,udigest,val):
  if what in ['cap','usage']:
    if val!=None:
        val = float(val)
    else:
        val = float(0)
  tab = capTables[utype]
  if action == 'set' and what.lower() == 'usage' and utype != 'device':
    return [0,'ERROR: Cannot update usage directly for %s, please update device'%(utype)]
  if action == 'set':
    cmd = "update %s set %s = '%s' where digest = '%s'"\
      %(tab,what,val,udigest)
    res = sql.run_insert_cmd(cmd,prnt=1)
    return res
  if action == 'get':
    cmd = "select %s from %s where digest = '%s'"\
      %(what,tab,udigest)
    res = sql.run_data_cmd(cmd)
    tmp = []
    tmp = list(res[0])
    if tmp[0]==float('inf'):
      tmp[0] = float(-1)
      try:
        return [1,tmp[0]]
      except:
        return [0,'ERROR: No Match']
  try:
    return [1,res[0][0]]
  except:
    return [0,'ERROR: No Match']

def HouseUsage(action,what,hid,val=None):
  utype = 'household'
  hdigest = get_digest(hid=hid)
  res = _updateUnit(utype,action,what,hdigest,val)
  if action == 'set':
    if res[0] == 1:
      return 'Success'
    else:
      return 'Error'
  elif action == 'get':
    return res

def UserUsage(action,what,hid,uid,val=None):
  utype = 'user'
  if uid == '':
    uid = default_user
  udigest = get_digest(hid=hid,uid=uid)
  res = _updateUnit(utype,action,what,udigest,val)
  if action == 'set':
    if res[0] == 1:
      return 'Success'
    else:
      return 'Error'
  elif action == 'get':
    return res

def DeviceUsage(action,what,hid,uid,did,val=None):
  utype = 'device'
  if uid == '':
    uid = default_user
  ddigest = get_digest(hid=hid,uid=uid,did=did)
  res = _updateUnit(utype,action,what,ddigest,val)
  if action == 'set':
    if res[0] == 1:
      return 'Success'
    else:
      return 'Error'
  elif action == 'get':
    return res

def DeviceUsagebymac(action,what,macaddr,val=None):
  utype = 'device'
  tab = capTables[utype]
  utab = unitTables[utype]
  cmd = "select digest from %s where '%s' = any(macid)"\
    %(utab,macaddr)
  res = sql.run_data_cmd(cmd)
  digest = ''
  try:
	digest = res[0][0]
  except:
    return [0,'ERROR: No Match']
  if action == 'set':
    if what == 'usage':
      cmd = "select %s from %s where digest = '%s'"\
             %(what,tab,digest)
      res = sql.run_data_cmd(cmd)
      if len(res) == 0 :
        return "Error"
      try:
        if res[1].lower() == 'error':
          return 'Error'
      except:
        ousage = float(res[0][0])
      if abs(ousage - float(val)) < 0.1:
        val = float(val) + 0.25
        val = str(val)
   
    cmd = "update %s set %s = '%s' where digest = '%s'"\
      %(tab,what,val,digest)
    res = sql.run_insert_cmd(cmd)
    if res[0]==1:
        return 'Successful update'
    else:
        return 'Error'
  if action == 'get':
    cmd = "select %s from %s where digest = '%s'"\
      %(what,tab,digest)
    res = sql.run_data_cmd(cmd)
  
  return res

def _getUnitstoDisable(unittype):
  tab = capTables[unittype]
  cmd = "select digest from %s where capped is True and cap <= usage"%(tab)
  res = sql.run_data_cmd(cmd,prnt=1)
  arr = []
  try:
    if res[0] == 0:
      return [0,'ERROR']
    for rec in res:
      arr.append(rec[0])
  except:
    return [0,'ERROR']
  return [1,arr]

def _getUnitstoEnable(unittype):
  tab = capTables[unittype]
  cmd = "select digest from %s where capped is False or cap > usage"%(tab)
  res = sql.run_data_cmd(cmd,prnt=1)
  arr = []
  try:
    if res[0] == 0:
      return [0,'ERROR']
    for rec in res:
      arr.append(rec[0])
  except:
    return [0,'ERROR']
  return [1,arr]

def _getUnitstoNotify(unittype):
  tab = capTables[unittype]
  utab = unitTables[unittype]
  cmd = "select digest from %s,%s where %s.notified is False and %s.notify is True and %s.cap * %s.notify_perc/100.0 > %s.usage"%(tab,utab,utab,utab,tab,utab,tab)
  res = sql.run_data_cmd(cmd,prnt=1)
  arr = []
  try:
    if res[0] == 0:
      return [0,'ERROR']
    for rec in res:
      arr.append(rec[0])
  except:
    return [0,'ERROR']
  return [1,arr]

def getHouseDisable():
  unittype = 'household'
  return _getUnitstoDisable(unittype)
def getUserDisable():
  unittype = 'user'
  return _getUnitstoDisable(unittype)
def getDeviceDisable():
  unittype = 'device'
  return _getUnitstoDisable(unittype)
def getHouseEnable():
  unittype = 'household'
  return _getUnitstoEnable(unittype)
def getUserEnable():
  unittype = 'user'
  return _getUnitstoEnable(unittype)
def getDeviceEnable():
  unittype = 'device'
  return _getUnitstoEnable(unittype)
def getHouseNotify():
  unittype = 'household'
  return _getUnitstoNotify(unittype)
def getUserNotify():
  unittype = 'user'
  return _getUnitstoNotify(unittype)
def getDeviceNotify():
  unittype = 'device'
  return _getUnitstoNotify(unittype)

def _CapExchange(tab,fdigest,tdigest,val):
  cmd1 = "update %s set cap = cap - %s where capped is True and cap != 'Infinity' and digest = '%s'"\
    %(tab,val,fdigest)
  cmd2 = "update %s set cap = cap + %s where capped is True and cap != 'Infinity' and digest = '%s'"\
    %(tab,val,tdigest)
  conn = sql.sqlconn()
  prnt = 1
  sql.run_insert_cmd("begin",conn=conn,prnt=prnt)
  for cmd in [cmd1,cmd2]:
    res = sql.run_insert_cmd(cmd,conn=conn,prnt=prnt)
    if res[0] == 0:
      sql.run_insert_cmd("rollback",conn=conn,prnt=prnt)
      return [0,"ERROR"]
  sql.run_insert_cmd("commit",conn=conn,prnt=prnt)
  return [1,"SUCCESS"]

def UserCapExchange(hid,fuid,tuid,val):
  unittype = 'user'
  tab = capTables[unittype]
  if tuid == '':
    tuid = default_user
  if fuid == '':
    fuid = default_user
  fdigest = get_digest(hid=hid,uid=fuid)
  tdigest = get_digest(hid=hid,uid=tuid)
  return _CapExchange(tab,fdigest,tdigest,val) 


def updateHouseMetaInfo(hid,address='',details='',photo=''):
    unittype = 'household'
    tab = unitTables[unittype]
    digest = get_digest(hid=hid)
    cmd = "update %s set "%(tab)
    if address == '' and details == '' and photo == '':
      return [1,["SUCCESS"]]
    if address != '':
      cmd = "%s address='%s',"%(cmd,address)
    if details != '':
      cmd = "%s details='%s',"%(cmd,details)
    if photo != '':
      cmd = "%s photo='%s',"%(cmd,photo)
    cmd = "%s where digest = '%s'"%(cmd[:-1],digest)
    res = sql.run_insert_cmd(cmd)
    try:
      return [1,["SUCCESS"]]
    except:
      return [0,['ERROR: Could not update table']]

def updateUserMetaInfo(hid,uid,name='',details='',photo='',did=None):
    if did == None:
      unittype = 'user'
      digest = get_digest(hid=hid,uid=uid)
    else:
      unittype = 'device'
      digest = get_digest(hid=hid,uid=uid,did=did)
    tab = unitTables[unittype]
    cmd = "update %s set "%(tab)
    if name == '' and details == '' and photo == '':
      return [1,["SUCCESS"]]
    if name != '':
      cmd = "%s name='%s',"%(cmd,name)
    if details != '':
      cmd = "%s details='%s',"%(cmd,details)
    if photo != '':
      cmd = "%s photo='%s',"%(cmd,photo)
    cmd = "%s where digest = '%s'"%(cmd[:-1],digest)
    res = sql.run_insert_cmd(cmd)
    try:
      return [1,["SUCCESS"]]
    except:
      return [0,['ERROR: Could not update table']]
 
#def updateUserMetaInfo_new(hid,uid,name='',details='',notify='',notifyperc='',notified='',photo='',role='',contact='',passwd='',did=None):
def updateUserMetaInfo_new(hid,uid,name='',details='',notify='',notifyperc='',notified='',photo='',role='',contact='',did=None):
    if did == None:
      unittype = 'user'
      digest = get_digest(hid=hid,uid=uid)
    else:
      unittype = 'device'
      digest = get_digest(hid=hid,uid='default',did=did)
    tab = unitTables[unittype]
    cmd = "update %s set "%(tab)
    if name == '' and details == '' and notify == '' and notifyperc == '' and notified == '' and photo == '' and role == '' and contact == '':
      return [1,["SUCCESS"]]
    if name != '':
      cmd = "%s name='%s',"%(cmd,name)
    if details != '':
      cmd = "%s details='%s',"%(cmd,details)
    if notify != '':
      cmd = "%s notify='%s',"%(cmd,notify)
    if notifyperc != '':
      cmd = "%s notifyperc='%s',"%(cmd,notifyperc)
    if notified != '':
      cmd = "%s notified='%s',"%(cmd,notified)
    if photo != '':
      cmd = "%s photo='%s',"%(cmd,photo)
    if role != '':
      cmd = "%s role='%s',"%(cmd,role)
    if contact != '':
      cmd = "%s contact='%s',"%(cmd,contact)
#    if passwd != '':
#        u = User.objects.get(username__exact=email)
#        u.set_password(passwd)
#        u.save()
    cmd = "%s where digest = '%s'"%(cmd[:-1],digest)
    res = sql.run_insert_cmd(cmd)
    try:
      return [1,["SUCCESS"]]
    except:
      return [0,['ERROR: Could not update table']]
 
def updateDeviceMetaInfo(hid,uid,did,name='',details='',photo=''):
    return updateUserMetaInfo(hid,uid,name=name,details=details,photo=photo,did=did)

def updateDeviceMetaInfo_new(hid,uid,did,name='',details='',notify='',notifyperc='',notified='',photo=''):
    return updateUserMetaInfo_new(hid,uid,name=name,details=details,notify=notify,notifyperc=notifyperc,notified=notified,photo=photo,did=did)

def loggingCalls(hid,method,params,date):
#digest = get_digest(hid=hid)
    tab = 'function_call_log'
    cmd = "insert into %s (caller,name,parameters,calltime) values('%s','%s','%s','%s')"\
      %(tab,hid,method,params,date)

    res = sql.run_insert_cmd(cmd)
    return [res]

def getHouseDigestFromUserID(uid):
    unittype = 'user'
    tab = unitTables[unittype]
    cmd = "select parentdigest from %s where id='%s'"%(tab,uid)
    res = sql.run_data_cmd(cmd)
    try:
      if res[0] == 0:
          return "ERROR: No match found"
    except:
      return ''
    #if len(res) == 0 or res[0] == 0:
     # return (0,"ERROR: No match found")
#return [1,res[0][0]]
    return res[0][0]

def check_hid_uid_match(hid,uid):
    unittype = 'user'
    tab = unitTables[unittype]
    cmd = "select digest from %s where id='%s'"%(tab,uid)
    res = sql.run_data_cmd(cmd)
    try:
      if res[0] == 0:
          return "ERROR: No match found"
    except:
      return ''
    #if len(res) == 0 or res[0] == 0:
     # return (0,"ERROR: No match found")
#return [1,res[0][0]]
    cmp_digest = get_digest(hid=hid,uid=uid) 
    if res[0][0]==cmp_digest:
        return True
    else:
        return False
 
def user_logs_ex(hid,start,end):
    cmd = "select * from function_call_log where caller='%s' and calltime between '%s' and '%s' and name like '%sUsage' and parameters like 'set,cap%s'"%(hid,start,end,'%','%')
    res = sql.run_data_cmd(cmd)

    try:
        if res[0] == 0:
            return "ERROR: No match found"
    except:
        return ''

    # converting from did to name
    rev_res = []
    for rec in res:
        tmp_tpl = ()
        if rec[1] == 'DeviceUsage':
            param_lst = rec[2].split(',')
            cmd1 = "select name from devices where id = '%s'" %(param_lst[4])
            name = sql.run_data_cmd(cmd1)
            if len(name) != 0:
                param_lst[4] = name[0][0]
            sep = ','
            mod_param = sep.join(param_lst)
            tmp_tpl = (rec[0],rec[1],mod_param,rec[3])
        else:
            tmp_tpl = rec
        rev_res.append(tmp_tpl)
    return rev_res

def user_logs(hid):
    cmd = "select * from function_call_log where caller='%s' and name like '%sUsage' and parameters like 'set,cap%s'"%(hid,'%','%')
    res = sql.run_data_cmd(cmd)
    try:
        if res[0] == 0:
            return "ERROR: No match found"
    except:
        return ''
    return res

def check_localhost(request):
    client_host = request.get_host()
    if client_host=="localhost":
        return True
    else:
        return False

def check_auth_and_uid(request,userid):
    if check_authed(request)==1 and (request.user.username==userid):
        return True
    else:
        return False

def check_auth_and_hid(request,hid):
    session_uid = request.user.username
    if check_hid_uid_match(hid,session_uid) is True and check_authed(request)==1:
        return True
    else:
        return False

def file_upload(request):
    path = ''
    res = ''
    upload = ''
    if request.method == 'POST':
        query_dict = request.POST
        hid = query_dict['hid']
        uid = query_dict['uid']
        did = ''
        did = query_dict['did']
#        did = query_dict['name']
#        print did
        if len(request.FILES.values()) != 0:
            name = request.FILES.values()[0].name
            size = request.FILES.values()[0].size
        
            # Check name length
            if len(name) > 50: 
                print 'Too long file size name'
                return HttpResponse("{error:too long}")
    
            # Check size
            if size > (5*1024*1024):
                print 'Too Big file'
                return HttpResponse("{error:too big}")
    
            for chunk in request.FILES.values()[0].chunks():
                upload = upload + chunk
            path = save_upload(upload,name)
            if path != '':
                pass
                if did!='':
                    res = updateDeviceMetaInfo_new(hid,uid,did,name='',details='',notify='',notifyperc='',notified='',photo=path)
                else:
                    res = updateUserMetaInfo_new(hid,uid,name='',details='',notify='',notifyperc='',notified='',photo=path,role='',contact='',did=None)
    
        else:
            return HttpResponse("{error}")
 
    return HttpResponse("{success:true}")

def save_upload(img_file,name):
    path = '/ucap_photos/' + name
    image = Image.open(StringIO.StringIO(img_file))
    thumb_size = 110,110
    image.thumbnail(thumb_size)
    image.save(path,"JPEG")
    return path

def update_house_startdate(hid,startdate):
    utype = 'household'
    tab = capTables[utype]
    digest = get_digest(hid=hid)
    cmd1 = "update %s set startdt = '%s' where digest = '%s'"%(tab,startdate,digest)
    cmd2 = "update %s set enddt = startdt + interval '1 month' where digest = '%s'"%(tab,digest)
    res = sql.run_insert_cmd(cmd1)
    res = sql.run_insert_cmd(cmd2)
    
    return [res]

def getOUI(oui_addr):
    out = []
    oui = OUI(oui_addr.encode("ascii"))
    for i in range(oui.reg_count):
        out.append(oui.registration(i).org)
    return out
