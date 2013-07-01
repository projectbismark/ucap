######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2013.6.20

# name: call_log_analysis.py
# desc: Python script for analyzing functiona call log.
#
######################################################

import os
import time
import sys
import re
import shlex, subprocess
import shutil
import socket
import string
import psycopg2
import pickle

LOCAL_DB_PORT = 54323

## Deployment and test database
DEPLOY = 1


####
def get_config(db_type, key):
    config = ''

    try: 
        if db_type == DEPLOY:
            config = open('server.conf').readlines()
        else:
            config = open('server_test.conf').readlines()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)

    for i in config:
        i = i.replace(" ","").replace('\n','').split("=")
        if i[0] == key:
            return i[1]
    return ''
###

###
def get_digest(cursor,hid=None,uid=None,did=None):
    if hid == None:
        return None
    if uid == None and did == None:
        pcmd = "'%s'"%(hid)
    elif did == None:
        pcmd = "'%s','%s'"%(uid,hid)
    else:
        if uid == None:
            return None
        pcmd = "'%s','%s','%s'"%(did,uid,hid)

    cmd = 'select md5(get_textid(%s))'%(pcmd)
    cursor.execute(cmd)
    res_tpl = cursor.fetchone()
    if res_tpl:
        return res_tpl[0]
    else:
        return ''
###


### 
def move_file_after_success(filename):
    # Move file when done with processing
    tmp_lst = (os.path.dirname(filename)).split('/')
    if os.path.exists(MOVE_DIR+'/'+tmp_lst[-1])==False:
        os.mkdir(MOVE_DIR+'/'+tmp_lst[-1])
    shutil.move(filename,MOVE_DIR+'/'+filename.lstrip(CHECK_DIR))
### 


def reconnect_to_database():
    while (1):
        sql_host = get_config(DEPLOY, 'sql_host').strip()
        sql_user = get_config(DEPLOY, 'sql_user').strip()
        sql_passwd = get_config(DEPLOY, 'sql_passwd').strip()
        sql_db = get_config(DEPLOY, 'sql_db').strip()

        try:
            conn = psycopg2.connect(database=sql_db, host=sql_host, user=sql_user,\
                            password=sql_passwd, port=LOCAL_DB_PORT)
            print 'CONNECTED!!'
            cursor = conn.cursor()
            break
        except:
            print 'Unable to connect to database. Continue trying..'
            time.sleep(5)
            continue

    return conn

############ FILE FORMAT ##########
# format_version
# build_id current timestamp
# hashed mac address        
#
# number of entries
# mac usage
# mac usage
# mac usage
# ...
###################################

### process ###
def process_file(filename, cursor, hid_str):
    # File open
    lines_lst = []
    digest_str = ''
    cmd_str = ''
    res_tpl = ()

    try: 
        fd = open(filename,'r')
        lines_lst = fd.readlines()
        fd.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
        
    if len(lines_lst) >= 5:
        usage_lst = lines_lst[MAC_START_POS:]

        # Get Hashed gateway mac addr
        hashed_gw_mc_str = lines_lst[HASHED_GW_POS].rstrip('/\n')
        
        # Get usage data.
        for line in usage_lst:
            mac_usage_lst = line.split(' ')
            if len(mac_usage_lst) >= 2:
                mac_str = mac_usage_lst[0].rstrip('/\n')
                usage_str = mac_usage_lst[1].rstrip('/\n')

                if not mac_str==hashed_gw_mc_str: # Don't insert if the mac is the gateway itself
                    print hid_str,mac_str,usage_str
                    try:
                        cmd = "SELECT devices.digest from devices,households where devices.macid='{%s}' and households.id='%s'"%(mac_str,hid_str)
                        cursor.execute(cmd)
                        res_tpl = cursor.fetchone()
                        if res_tpl: # Device exists in the database
                            digest_str = res_tpl[0]
                        else:
                            parentdigest_str = get_digest(cursor,hid_str,'default')
                            cmd = "INSERT into devices (id,name,details,notify,notifyperc,notified,photo,macid,parentdigest) values('%s','%s','N/A','f','80','f','','{%s}','%s')"\
                                   %(mac_str,mac_str,mac_str,parentdigest_str)

                            cursor.execute(cmd)
                            digest_str = get_digest(cursor,hid_str,'default',mac_str)
                            print 'New Device Added'
                        if not digest_str=='':
                            cmd = "UPDATE device_caps_curr set usage=%s where digest='%s'" %(usage_str,digest_str)
                            cursor.execute(cmd)
                            print 'Usage Updated'
#                    except:
                    except Exception as err:
                        sys.stderr.write('ERROR: %s\n' % str(err))
                        print 'Failed in database command sequence: '+str(err.pgcode)
                        if err.pgcode is not None:
                            if err.pgcode[:2] == '08': # Connection exception
                                time.sleep(1)
                                return -1
                        else:
                            return -2

#        # Move file when done with processing
#        tmp_lst = (os.path.dirname(filename)).split('/')
#        if os.path.exists(MOVE_DIR+'/'+tmp_lst[-1])==False:
#            os.mkdir(MOVE_DIR+'/'+tmp_lst[-1])
#        shutil.move(filename,MOVE_DIR+'/'+filename.lstrip(CHECK_DIR))
##        shutil.copy(filename,MOVE_DIR+'/'+filename.lstrip(CHECK_DIR))

    else:
        print 'Wrong format'
        print lines_lst

    return 0

def process_existing(conn, cursor):
    tmp_lst = []
    file_lst = []

    # Sweep the Check directorty, and process any existing files first.
    dir_lst = os.listdir(CHECK_DIR)
    for dirc in dir_lst:
        if dirc!='OWC43DC7B0AE63' and dirc!='OWC43DC7A37C0D':
            if os.path.isdir(CHECK_DIR+'/'+dirc):
                tmp_lst = (CHECK_DIR+'/'+dirc).split('/')
                # if new directory, make it on moved_dir.
                if os.path.exists(MOVE_DIR+'/'+tmp_lst[-1])==False:
                    os.mkdir(MOVE_DIR+'/'+tmp_lst[-1])
                file_lst = os.listdir(CHECK_DIR+'/'+dirc)
                for files in file_lst:
                    file_name_str = CHECK_DIR+'/'+dirc+'/'+files
                    hid_time_seq = file_name_str.split('-')
                    hid_time_seq = file_name_str.split('/')
                    hid_str = hid_time_seq[-1]
                    tmp_lst = hid_str.split('-')
                    hid_str = tmp_lst[0]
                    
                    # Check hid in database
                    cmd_1 = "SELECT digest from households where id = '%s'"%(hid_str)
                    try: 
                        cursor.execute(cmd_1)
                        res_tpl_1 = cursor.fetchone()
                        if res_tpl_1 is None: # router does not exist in the database
                          print 'Oh. that HID does not exist in database: %s'%(hid_str)
                          break

                    except Exception as err:
                        sys.stderr.write('ERROR: %s\n' % str(err))
                        print 'Failed in database command sequence: '+str(err.pgcode)
                        if err.pgcode is not None:
                            if err.pgcode[:2] == '08': # Connection exception
                                time.sleep(1)
                                return -1
                        else:
                            return -2

                    r_check = process_file(CHECK_DIR+'/'+dirc+'/'+files, cursor, hid_str)
                    if r_check == -1: # Connection error when executing database command.
                        conn = reconnect_to_database();
                        cursor = conn.cursor()
                        return -1

                    # None, or something error than connection error..
                    elif r_check == -2:
                        try:
                            conn.rollback()
                            break
                        except Exception:
                            conn = reconnect_to_database();
                            cursor = conn.cursor()
                            return -1
                    else: # Execution success. Now try to commit changes.
                        try:
                            conn.commit()
                            # Success!! Now, move the file.
                            ffname = CHECK_DIR+'/'+dirc+'/'+files
                            move_file_after_success(ffname)
    
                        except Exception as err:
                            print "Commit error:" + str(err)
                            conn = reconnect_to_database();
                            cursor = conn.cursor()
                            return -1

    return 0                            

""" call log analysis """
def call_log_analysis(cursor):
  
  cmd = "SELECT * FROM function_call_log"
  cursor.execute(cmd)
  tuples_lst = cursor.fetchall()

  callers_map = {}
  functions_map = {}
  cf_combination_map = {}

  for t in tuples_lst:
    caller_router = t[0]
    function_name = t[1]
    params = t[2]
    time = t[3]

    # callers
    if callers_map.has_key(caller_router):
      callers_map[caller_router] = callers_map[caller_router] + 1
    else:
      callers_map[caller_router] = 1
 
    # functions  
    if functions_map.has_key(function_name):
      functions_map[function_name] = functions_map[function_name] + 1
    else:
      functions_map[function_name] = 1
 
    # combination
    if cf_combination_map.has_key((caller_router,function_name)):
      cf_combination_map[(caller_router,function_name)] = cf_combination_map[(caller_router,function_name)] + 1
    else:
      cf_combination_map[(caller_router,function_name)] = 1
 
  nums_of_logs = len(tuples_lst)
  print nums_of_logs
  print len(callers_map)
  print len(functions_map)

  return tuples_lst,callers_map,functions_map,cf_combination_map


""" analze """
def save_data(tuples_lst, c_map, f_map, cf_map):

  fp = open('./tuples_lst.p', 'wb')
  pickle.dump(tuples_lst, fp)
  fp.close()

  fp = open('./callers_map.p', 'wb')
  pickle.dump(c_map, fp)
  fp.close()

  fp = open('./functions_map.p', 'wb')
  pickle.dump(f_map, fp)
  fp.close()

  fp = open('./combination_map.p', 'wb')
  pickle.dump(cf_map, fp)
  fp.close()

    
### main ###
def main():

    while (1):
        # Connection establishment to DB
        sql_host = get_config(DEPLOY, 'sql_host').strip()
        sql_user = get_config(DEPLOY, 'sql_user').strip()
        sql_passwd = get_config(DEPLOY, 'sql_passwd').strip()
        sql_db = get_config(DEPLOY, 'sql_db').strip()
    
        try:
            conn = psycopg2.connect(database=sql_db, host=sql_host, user=sql_user, password=sql_passwd, port=LOCAL_DB_PORT)
            print 'CONNECTED!!'
            break
        except:
            print 'Unable to connect to database. Continue trying..'
            time.sleep(5)
            continue
    cursor = conn.cursor()
  
    tuples_lst, callers_map, functions_map, cf_combination_map = call_log_analysis(cursor)

    save_data(tuples_lst, callers_map, functions_map, cf_combination_map)

###
if __name__ ==  '__main__':
    main()
###
