######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2012.04.05

# name: del_user.py
# desc: Python script for deleting users to uCap.
#
######################################################

import os
import sys
import re
from django.conf import settings
settings.configure(DEBUG=False, TEMPLATE_DEBUG=False, TEMPLATE_DIRS=(''))

from jsonrpc.proxy import ServiceProxy

REMOTE_JSON = 'https://localhost/json/json/'

def deluser_params():
    client = ServiceProxy(REMOTE_JSON)
    router_id = ''

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

        result = client.ucap.check_uid_existence(router_id, user_id)
        if result['result'][1]=='f':
            print 'Wrong User ID. Input again.'
            continue
        else:
            break

    # Review information
    print "\n\nPlease review and verify inputs. No turning back after this!"
    print "\n* Router ID: %s\n* User ID: %s\n"%(router_id,user_id)

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
        result = client.ucap.delUser(router_id,user_id)
        print 'User deleted.'
        return 0
    except:
        print 'JSONRPC Failed. Abort'
        return -1
#### 

## main ##
def main():

    ret_val = 0
    ret_val = deluser_params()
    while ret_val==-2:
        ret_val = deluser_params()
    if ret_val==-1:
        sys.exit(1)

###
if __name__ ==  '__main__':
    main()
###
