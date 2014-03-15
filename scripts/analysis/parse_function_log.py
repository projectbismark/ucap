######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2013.6.20

# name: parse_function_log.py
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
import copy
from optparse import OptionParser

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


def find_router_by_param(params, cursor):
  param_list = str(params).split(',')
  caller_router = 'failed'

  for p in param_list:
    if p.startswith('OW') is True:    # router ID here.
      caller_router = p
      break
    elif p.count('@') is True:        # possibly email address
      cmd = "SELECT households.id from households,users where parentdigest=households.digest AND users.id='"+p+"'"
      cursor.execute(cmd)
      tuples_lst = cursor.fetchall()  # Table entrie in tuple format
      if len(tuples_lst) > 0:
        if len(tuples_lst[0]) > 0:
          caller_router = tuples_lst[0][0]
  return caller_router

""" call log analysis """
def call_log_analysis(cursor):
  
  cmd = "SELECT * FROM function_call_log"
  cursor.execute(cmd)
  tuples_lst = cursor.fetchall()  # Table entrie in tuple format

  callers_map = {}          # { RouterID :  Number of logs }
  functions_map = {}        # { FunctionName : Number of logs }
  cf_combination_map = {}   # { ((RouterID, FunctionName) : Number of logs }

  fixed_tuples_lst = copy.deepcopy(tuples_lst)                               

  for idx,t in enumerate(tuples_lst):
    caller_router = t[0]
    function_name = t[1]
    params = t[2]
    time = t[3]

    # If router field seems wrong, find the router by inspecting params.
    if len(caller_router) < 5:
      caller_router = find_router_by_param(params, cursor)
    if len(caller_router) < 5:
      print 'something wrong with router id name'
      sys.exit(1)

    fixed_tuples_lst[idx] = (caller_router, t[1],t[2],t[3])

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

#  return tuples_lst,callers_map,functions_map,cf_combination_map
  return fixed_tuples_lst,callers_map,functions_map,cf_combination_map


""" analyze """
def save_data(tuples_lst, c_map, f_map, cf_map, output_dir):

  fp = open(output_dir + 'tuples_lst.p', 'wb')
  pickle.dump(tuples_lst, fp)
  fp.close()

  fp = open(output_dir + 'callers_map.p', 'wb')
  pickle.dump(c_map, fp)
  fp.close()

  fp = open(output_dir + 'functions_map.p', 'wb')
  pickle.dump(f_map, fp)
  fp.close()

  fp = open(output_dir + 'combination_map.p', 'wb')
  pickle.dump(cf_map, fp)
  fp.close()

  
### main ###
def main():

  #################################################################################
  # Before execution, establish SSH tunnel.
  #  $ ssh -R 54323:localhost:5432 paix.noise.gatech.edu -o ServerAliveInterval=60
  #################################################################################


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

  ## Options
  desc = ( 'Parse ucap UI call log. Make pickled data' )
  usage = ( '%prog [options]\n'
            '(type %prog -h for details)' )
  op = OptionParser( description=desc, usage=usage )
  op.add_option( '--output', '-o', action="store", \
                 dest="output", help = "Output directory for pickled data" )

  ## Check option     
  options, args = op.parse_args()
  if options.output is None:
    print 'Wrong number of arguments. exit'
    return
    
  ## attach / if not there    
  output_dir = options.output
  if output_dir.endswith('/') is False:
    output_dir = output_dir + '/'

  ## Check access
  if os.access(output_dir, os.R_OK) is False:
    print 'Cannot access output dir. Maybe does not exist? Exit.'
    return

  ## Connect
  cursor = conn.cursor()

  ## Start fetch, store.
  tuples_lst, callers_map, functions_map, cf_combination_map = call_log_analysis(cursor)

  ## Save as pickled data.
  save_data(tuples_lst, callers_map, functions_map, cf_combination_map, output_dir)

###
if __name__ ==  '__main__':
  main()
###
