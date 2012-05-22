######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2012.04.05

# name: add_user.py
# desc: Python script for adding new users to uCap.
#
######################################################

import os
import sys
import re
from django.conf import settings
settings.configure(DEBUG=False, TEMPLATE_DEBUG=False, TEMPLATE_DIRS=(''))

from jsonrpc.proxy import ServiceProxy

REMOTE_JSON = 'https://localhost/json/json/'

def adduser_params():
    client = ServiceProxy(REMOTE_JSON)

    while 1:
        router_id = raw_input("\nEnter Router ID: ")
        result = client.ucap.check_hid_existence(router_id)
        if result['result'][1]=='f':
            print 'Wrong Router ID. Input again.'
            continue
        else:
            break

    while 1:
        user_id = raw_input("\nEnter User ID (as email address): ")
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", user_id):
            print 'Invalid email address. Input again.'
            continue
        else:
            break

    while 1:
        role = raw_input("\nEnter Role of User (admin or user): ")
        if role!='admin' and role!='user':
            print 'Wrong role. Type either admin or user. Input again.'
            continue
        else:
            break

    while 1:
        passwd = raw_input("\nEnter Password: ")
        if passwd=='':
            print 'Empty password. Input again.'
            continue
        else:
            break

    user_name = raw_input("\nEnter Name: ")
    details = raw_input("\nEnter Details (some info): ")
    
    notify = 'f'
    notifyperc = '80'
    notified = 'f'
    photofilepath = ''

    # Review information
    print "\n\nPlease review and verify inputs. No turning back after this!"
    print "\n* Router ID: %s\n* User ID: %s\n* Role: %s\n* Password: %s\n* Name: %s\n* Details: %s\n"%(router_id,user_id,role,passwd, user_name,details)

    while 1:
        yes_enter = raw_input("\nIs everything correct? (y/n): ")
        if yes_enter=='y' or yes_enter=='yes':
            break
        elif yes_enter=='n' or yes_enter=='no':
            print "Starting over...."
            return -2
        else:
            continue
    try:
        client.ucap.addUser(router_id, user_id, user_name, details, user_id, passwd, role, notify, notifyperc, notified, photofilepath)
        print 'User Added.'
        return 0
    except:
        print 'JSONRPC Failed. Abort'
        return -1
#### 

## main ##
def main():

    ret_val = 0
    ret_val = adduser_params()
    while ret_val==-2:
        ret_val = adduser_params()
    if ret_val==-1:
        sys.exit(1)

###
if __name__ ==  '__main__':
    main()
###
