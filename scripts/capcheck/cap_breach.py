######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2011.08.01

# name: cap_breach.py
# desc: Python script for checking for cap limit reached,
#   and sending notification to Resonance controller, 
#   if reached.
#
######################################################

import os
import time
import pg
import sys
import time
import shlex, subprocess
from django.conf import settings
settings.configure(DEBUG=False, TEMPLATE_DEBUG=False, TEMPLATE_DIRS=(''))

from jsonrpc.proxy import ServiceProxy
import smtplib
from email.mime.text import MIMEText

#REMOTE_JSON = 'http://bourbon.gtnoise.net/json/json/'
REMOTE_JSON = 'https://localhost/json/json/'
LOCAL_SMTP_PORT = 25

# email related
EMAIL_SENDER = 'ucap-admin@mail.noise.gatech.edu'
EMAIL_RECEIVER = ''
EMAIL_SUBJECT = '[uCap] Cap reached notification'
EMAIL_BASE_CONTENT = 'This is an automated message from uCap. Do not reply to this address.\n\n'
EMAIL_END_CONTENT = 'Visit http://projectbismark.net to monitor and manage usage. \n\n'

SENDER_ID = '01'
# enable or disable flow
ACTION_NOTIFY = '02'
ACTION_BLOCK = '01'
ACTION_ALLOW = '00'

# target
TARGET_HOUSEHOLD = 1
TARGET_USER = 2
TARGET_DEVICE = 3


###
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
###


###
def send_noti_email(action,recv_str,percent_str,did_str):
    email_content = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n")%(EMAIL_SENDER,recv_str,EMAIL_SUBJECT)
    email_content = email_content + EMAIL_BASE_CONTENT
    if action==ACTION_NOTIFY:
        email_content = email_content +"Device '%s' has reached %s of its capacity:\n\n"%(did_str,percent_str)
    elif action==ACTION_BLOCK:
        email_content = email_content +"Device '%s' has reached its max capacity.\n\n"%(did_str)

#    # Fill with newly blocked devices.
#    for newmac in new_block_lst:
#        dname_json = client.ucap.deviceNameBymac(newmac)
#        print dname_json
#        email_content = email_content + dname_json + '\n'
     
    # attach end content
    email_content = email_content + EMAIL_END_CONTENT

    # send mail
    try: 
        email = smtplib.SMTP('mail.noise.gatech.edu',LOCAL_SMTP_PORT)
        email.sendmail(EMAIL_SENDER, recv_str, email_content)
        email.quit()
        return 0
    except:
        print 'Failed SMTP connection, sendmail, quit.'
        return -1

####
def take_action(conn, action, target):
    print 'Notified'
    client = ServiceProxy(REMOTE_JSON)
    digest_lst = []
    hid_str = ''
    uid_str = ''
    did_str_lst = []
    tmp_lst = []
    mac_lst = []

    # Check Client connection
    try:
        client.ucap.getHouseEnable()
    except:
        print 'Connection to JSONRPC server failed. return'
        return

    # House hold               
    if target==TARGET_HOUSEHOLD:
        if action==ACTION_ALLOW:
            tmp_lst = client.ucap.getHouseEnable()
            print 'Enable House notification'
        else:
            tmp_lst = client.ucap.getHouseDisable()
            print 'Disable House notification'
        # extract house digest ids
        if tmp_lst['result'][0]==1:
            digest_lst = tmp_lst['result'][1]
        # for each digest, get id and then mac.
        for dig in digest_lst:
            tmp_lst = client.ucap.getHouseInfo(dig)
            if tmp_lst['result'][0]==1:
                hid_str = tmp_lst['result'][1]
            tmp_lst = client.ucap.getHouseDeviceMacs(hid_str)
            if tmp_lst['result'][0]==1: # if there are macs, extend mac_lst
                tmp_lst = tmp_lst['result'][1]
                mac_lst.extend(tmp_lst)

    # User    
    elif target==TARGET_USER:
        if action==ACTION_ALLOW:
            tmp_lst = client.ucap.getUserEnable()
            print 'Enable User notification'
        else:
            tmp_lst = client.ucap.getUserDisable()
            print 'Disable User notification'
        # extract user digest ids
        if tmp_lst[0]==1:
            digest_lst = tmp_lst[1]
        # for each digest, get device macs associated with it.
        for dig in digest_lst:
            tmp_lst = client.ucap.getUserInfo(dig) 
            if tmp_lst[0]==1:
                hid_str = tmp_lst[1][0]
                uid_str = tmp_lst[1][1]
            tmp_lst = client.ucap.getUserDeviceMacs(hid_str, uid_str)
            if tmp_lst[0]==1: # if there are macs, extend mac_lst
                tmp_lst = tmp_lst[1]
                mac_lst.extend(tmp_lst)

    # Device
    elif target==TARGET_DEVICE:
        if action==ACTION_ALLOW:
            tmp_lst = client.ucap.getDeviceEnable()
            print 'Enable Device notification'
        elif action==ACTION_NOTIFY:
            tmp_lst = client.ucap.getDeviceNotify()
            print 'Notify User notification'
        else:
            tmp_lst = client.ucap.getDeviceDisable()
            print 'Disable Device notification'
        # extract device digest ids
        if tmp_lst['result'][0]==1:
            digest_lst = tmp_lst['result'][1]
        # for each digest, get device macs associated with it.
        tmp2_lst = []
        tmp3_lst = []
        for dig in digest_lst:
            tmp_lst = client.ucap.getDeviceInfo(dig)
            did_str_lst = []
            if tmp_lst['result'][0]==1:
                hid_str = tmp_lst['result'][1][1][0]
                uid_str = tmp_lst['result'][1][1][1]
                did_str_lst.append(tmp_lst['result'][1][2])

                # Sending email
                if action!=ACTION_ALLOW:
                    tmp2_lst = client.ucap.getUserMetaInfo(hid_str,uid_str)
                    tmp3_lst = client.ucap.getDeviceMetaInfo_ex(hid_str,uid_str,did_str_lst[0])
                    if tmp2_lst['result'][0]==1 and tmp3_lst['result'][0]==1:
                        recv_str = tmp2_lst['result'][1][8]
                        dev_name = tmp3_lst['result'][1][1]
                        percent_str = tmp3_lst['result'][1][4]
                        email_notified = tmp3_lst['result'][1][5]
                        if email_notified=='f':
                            ret = send_noti_email(action,recv_str,percent_str,dev_name)
                            # Set that device is notified.
                            if not ret<0:
                                client.ucap.updateDeviceMetaInfo_ex(hid_str,uid_str,did_str_lst[0],'','','','','t','')
              
                # If allowing, clear off the "notified" field
                else:
                    client.ucap.updateDeviceMetaInfo_ex(hid_str,uid_str,did_str_lst[0],'','','','','f','')

            tmp_lst = client.ucap.getDeviceMacs(hid_str, uid_str, did_str_lst)
            if tmp_lst['result'][0]==1: # if there are macs, extend mac_lst
                tmp_lst = tmp_lst['result'][1]
                mac_lst.extend(tmp_lst)

    # Unknown Target. Something wrong.
    else: 
        print 'Unknown Target. It Is: ' + target

    # Delete all duplicates. Only python 2.5 and later version required to make this work.
    mac_lst = list(set(mac_lst))

    if action!=ACTION_NOTIFY:
        # Send msg to OpenFlow Controller
        for mac in mac_lst:
            # Send notification to Resonance
            exec_str = 'python sendy.py '+SENDER_ID+' '+mac+ ' '+action
            p = subprocess.Popen(exec_str, shell=True)
            p.communicate(0) # wait until execute is complete
####

#### 
def check_notify(conn):
    enable = 0
    target = 0

    # get notify
    while 1:
        try:
            noti_tup = conn.getnotify() 
        except:
            print 'getnotify() failed\n'
            conn.close()
            sys.exit(1)

        # if notified,
        if noti_tup:
            if noti_tup[0]=='cap_breached_disable_household':
                take_action(conn, ACTION_BLOCK,TARGET_HOUSEHOLD)
            elif noti_tup[0]=='cap_breached_disable_user':
                take_action(conn, ACTION_BLOCK,TARGET_USER)
            elif noti_tup[0]=='cap_breached_disable_device':
                take_action(conn, ACTION_BLOCK,TARGET_DEVICE)
            elif noti_tup[0]=='cap_updated_enable_household':
                take_action(conn, ACTION_ALLOW,TARGET_HOUSEHOLD)
            elif noti_tup[0]=='cap_updated_enable_user':
                take_action(conn, ACTION_ALLOW,TARGET_USER)
            elif noti_tup[0]=='cap_updated_enable_device':
                take_action(conn, ACTION_ALLOW,TARGET_DEVICE)
            elif noti_tup[0]=='cap_status_enable_household':
                take_action(conn, ACTION_ALLOW,TARGET_HOUSEHOLD)
            elif noti_tup[0]=='cap_status_enable_user':
                take_action(conn, ACTION_ALLOW,TARGET_USER)
            elif noti_tup[0]=='cap_status_enable_device':
                take_action(conn, ACTION_ALLOW,TARGET_DEVICE)
            elif noti_tup[0]=='notify_user':
                take_action(conn, ACTION_NOTIFY,TARGET_USER)
            else: 
                print 'unknown notification. It is: '+noti_tup[0]

        time.sleep(1)
####

## main ##
def main():
    sql_host = get_config('sql_host').strip()
    sql_user = get_config('sql_user').strip()
    sql_passwd = get_config('sql_passwd').strip()
    sql_db = get_config('sql_db').strip()

    print sql_host,sql_user,sql_passwd,sql_db
    
    try:
        conn = pg.connect(host=sql_host, dbname=sql_db, user=sql_user, passwd=sql_passwd)
    except:
        print 'Connection to DB %s failed.\n' % (sql_db)
        sys.exit(1)
    
    try:
        conn.query('LISTEN CAP_BREACHED_DISABLE_HOUSEHOLD')
        conn.query('LISTEN CAP_BREACHED_DISABLE_USER')
        conn.query('LISTEN CAP_BREACHED_DISABLE_DEVICE')
        conn.query('LISTEN CAP_UPDATED_ENABLE_HOUSEHOLD')
        conn.query('LISTEN CAP_UPDATED_ENABLE_USER')
        conn.query('LISTEN CAP_UPDATED_ENABLE_DEVICE')
        conn.query('LISTEN CAP_STATUS_ENABLE_HOUSEHOLD')
        conn.query('LISTEN CAP_STATUS_ENABLE_USER')
        conn.query('LISTEN CAP_STATUS_ENABLE_DEVICE')

        # for n% notification.       
        conn.query('LISTEN NOTIFY_USER')

    except:
        print 'LISTEN query failed'
        sys.exit(1)

    check_notify(conn)
       
###
if __name__ ==  '__main__':
    main()
###
