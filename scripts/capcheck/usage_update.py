######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2012.3.6

# name: usage_update.py
# desc: Python script for updating data usage,
#       inserting to database.
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
import pyinotify
import psycopg2

CHECK_DIR = '/data/users/bismark/data/http_uploads/passive-frequent'
MOVE_DIR = '/data2/users/hyojoon/bismark/usage_data_moved'
CHECK_COUNTER = 6
LOCAL_DB_PORT = 54322

####
HASHED_GW_POS = 2
MAC_START_POS = 5

## Deployment and test database
DEPLOY = 1
TEST = 2


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

### main ###
def main():

    while (1):
        # Connection establishment to DB
        sql_host = get_config(DEPLOY, 'sql_host').strip()
        sql_user = get_config(DEPLOY, 'sql_user').strip()
        sql_passwd = get_config(DEPLOY, 'sql_passwd').strip()
        sql_db = get_config(DEPLOY, 'sql_db').strip()
    
    #    sql_host_test = get_config(TEST, 'sql_host').strip()
    #    sql_user_test = get_config(TEST, 'sql_user').strip()
    #    sql_passwd_test = get_config(TEST, 'sql_passwd').strip()
    #    sql_db_test = get_config(TEST, 'sql_db').strip()
        try:
            conn = psycopg2.connect(database=sql_db, host=sql_host, user=sql_user, password=sql_passwd, port=LOCAL_DB_PORT)
            print 'CONNECTED!!'
            break
        except:
            print 'Unable to connect to database. Continue trying..'
            time.sleep(5)
            continue
        
    cursor = conn.cursor()
    testvar = 'bka'


    # process existing files
    process_existing(conn,cursor)
    print 'Done with Existing Files!'

    # Pyinotify
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE

    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CREATE(self,event):
            print 'Created:', event.pathname
            self.conn = conn
            self.cursor = cursor
            result = 0

            # Get household id.
            hid_time_seq = event.pathname.split('-')
            hid_time_seq = event.pathname.split('/')
            hid_str = hid_time_seq[-1]
            tmp_lst = hid_str.split('-')
            hid_str = tmp_lst[0]

            # if new directory, make it on moved_dir, and pass.
            if os.path.isdir(event.pathname):
               tmp_lst = (event.pathname).split('/')
               if os.path.exists(MOVE_DIR+'/'+tmp_lst[-1])==False:
                 os.mkdir(MOVE_DIR+'/'+tmp_lst[-1])

            print tmp_lst[-1]
            if tmp_lst[-1] == 'OWC43DC7A37C0D':
                return

#            # if regular file, process it.
#            else:
#                count_check = process_file(event.pathname, self.cursor,  hid_str)
#                if count_check == -1: # Connection error when executing database command.
#                    self.conn = reconnect_to_database();
#                    self.cursor = self.conn.cursor()
#
#                else: # Execution success. Now try to commit changes.
#                    try:
#                        conn.commit()
#                        # Success!! Now, move the file.
#                        ffname = event.pathname
#                        move_file_after_success(ffname)
#    
#                    except Exception, err:
#                        print "Commit error:" + str(err)
#                        self.conn = reconnect_to_database();
#                        self.cursor = self.conn.cursor()
#
            print "Start processing existing stuff again"
            result = process_existing(self.conn,self.cursor)
            
            # Error with connection
            if result == -1:
              self.conn = reconnect_to_database();
              self.cursor = self.conn.cursor()

                

    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(CHECK_DIR,mask,rec=True)

    # Start
    notifier.loop()
###

###
if __name__ ==  '__main__':
    main()
###
