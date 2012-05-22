######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2012.04.05

# name: add_home.py
# desc: Python script for adding new households to uCap.
#
######################################################

import os
import sys
import re
from django.conf import settings
settings.configure(DEBUG=False, TEMPLATE_DEBUG=False, TEMPLATE_DIRS=(''))

from jsonrpc.proxy import ServiceProxy

REMOTE_JSON = 'https://localhost/json/json/'

def addhome_params():
    client = ServiceProxy(REMOTE_JSON)

    while 1:
        router_id = raw_input("\nEnter Router ID: ")
        if router_id=='':
            print 'Empty address. Input again.'
            continue

        result = client.ucap.check_hid_existence(router_id)
        if result['result'][1]=='t':
            print 'This Router ID already exists. Input again.'
            continue
        else:
            break

    while 1:
        address = raw_input("\nEnter Home Address: ")
        if address=='':
            print 'Empty address. Input again.'
            continue
        else:
            break

    while 1:
        details = raw_input("\nEnter Description: ")
        if details=='':
            print 'Empty description. This is good for identifcation. Input again.'
            continue
        else:
            break

    notify = 'f'
    notifyperc = '80'
    notified = 'f'
    photofilepath = ''

    # Review information
    print "\n\nPlease review and verify inputs. No turning back after this!"
    print "\n* Router ID: %s\n* Home Address: %s\n* Description: %s\n"%(router_id,address,details)

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
        res = client.ucap.addHouse(router_id, address, details, photofilepath)
        print res
        print 'Home Added.'
        return 0
    except:
        print 'JSONRPC Failed. Abort'
        return -1
#### 

## main ##
def main():

    ret_val = 0
    ret_val = addhome_params()
    while ret_val==-2:
        ret_val = addhome_params()
    if ret_val==-1:
        sys.exit(1)

###
if __name__ ==  '__main__':
    main()
###
