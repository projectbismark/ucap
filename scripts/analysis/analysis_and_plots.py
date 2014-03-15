######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2013.6.20

# name: analysis_and_plots.py
# desc: Python script for analyzing and plotting
#
######################################################

import pickle
import numpy as np
import operator
import string
import pickle
import sys
import re
import time
import os
import sqlite3 as db
import shlex, subprocess
import hashlib
import xml.etree.ElementTree as ET
from multiprocessing import Process
from multiprocessing import Pool
from collections import namedtuple
from datetime import datetime
import tarfile
import matplotlib as mpl
mpl.use('PS')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from numpy.random import normal
import numpy as np
import pytz
from optparse import OptionParser
#import dpkt
from matplotlib.patches import ConnectionPatch
import struct
import copy
from socket import *

mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif', 'sans-serif': ['Times'], 'size': 9})
mpl.rc('figure', figsize=(3.33, 7.06))
mpl.rc('axes', linewidth=0.5)
mpl.rc('patch', linewidth=0.5)
mpl.rc('lines', linewidth=0.5)
mpl.rc('grid', linewidth=0.25)


focus_list = []

sa_list = []

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



def is_sa_router(router_id):
  needle = router_id + '\n'
  global sa_list
  if needle in sa_list:
    return True
  else:
    return False

def create_figure(title, xlabel, ylabel):
  figure = plt.figure(figsize=(12.3,6))
  plt.title(title, fontsize=27)
  plt.xlabel(xlabel, fontsize=23)
  plt.ylabel(ylabel, fontsize=25, ma='center')

  return plt


def make_lastlog_time(t_lst, input_dir):
#####
# Table "public.function_call_log"
#    Column   |            Type             | Modifiers
# ------------+-----------------------------+-----------
#  caller     | id_t                        |
#  name       | fname_t                     |
#  parameters | fparam_t                    |
#  calltime   | timestamp without time zone (2013-04-02 19:01:34) |
#####

  
  timestamp_to_routers_map = {}  ## { Timestamp : [routerIDs,] }

  for t in t_lst:
    ts_str =  str(t[3])
    router_str = str(t[0])
    if len(router_str) < 10:
      continue

    date_int = int(ts_str[:10].replace('-',''))
    if timestamp_to_routers_map.has_key(date_int) is True:
      if timestamp_to_routers_map[date_int].count(router_str) == 0:
        timestamp_to_routers_map[date_int].append(router_str)
      else:
        pass
    else:
      timestamp_to_routers_map[date_int] = [router_str,]

  tkeys = sorted(timestamp_to_routers_map.keys())

  # Save
  fp = open(input_dir + 'timestamp_map.p', 'wb')
  pickle.dump(timestamp_to_routers_map, fp)
  fp.close()

def plot_work(t_lst, c_map, f_map, cf_map, output):
  callers = []
  functions = []

  # Callers
  xa = []
  ya = []

  plt = create_figure("Number of logs for each router", "Routers", "Number of logs")

  for caller in c_map:
    callers.append(caller)
    xa.append(caller)
    ya.append(c_map[caller])
    
  ind = np.arange(len(xa))
  plt.yscale('log')
  b1 = plt.bar(ind,ya, 0.25, color='red')
  ff = plt.gcf()
  ff.subplots_adjust(bottom=0.35)

  plt.xticks(ind,xa, rotation=80)
  plt.savefig('./callers.eps')

  # Functions
  xa = []
  ya = []
  plt = create_figure("Number of calls for each function", "Functions", "Number of calls")

  for function in f_map:
    functions.append(function)
    xa.append(function)
    ya.append(f_map[function])
    
  ind = np.arange(len(xa))
  plt.yscale('log')
  b1 = plt.bar(ind,ya, 0.25, color='red')
  plt.xticks(ind,xa, rotation=80)
  ff = plt.gcf()
  ff.subplots_adjust(bottom=0.35)

  plt.savefig('./functions.eps')

  # Combination
  xa = []
  ya = []

  sa_functions_map = {}
  usa_functions_map = {}

  for c in c_map:
    if is_sa_router(c) is True:
      country = 'SA'
    else:
      country = 'USA'

    tmp_fmap = {}
    xa = []
    ya = []
    for cf in cf_map:
      if c == cf[0]:
        tmp_fmap[cf[1]] = cf_map[cf]

    plt = create_figure(c, "Functions", "Number of calls")

    for function in f_map:
      xa.append(function)
      if tmp_fmap.has_key(function) is True:
        ya.append(tmp_fmap[function])
        fvalue = tmp_fmap[function]
      else:
        ya.append(0)
        fvalue = 0

      if country == 'SA':
        if sa_functions_map.has_key(function) is True:
          tmp_list = sa_functions_map[function]
          tmp_list.append(fvalue)
          sa_functions_map[function] = tmp_list
        else:
          sa_functions_map[function] = [fvalue,]

      else:
        if usa_functions_map.has_key(function) is True:
          tmp_list = usa_functions_map[function]
          tmp_list.append(fvalue)
          usa_functions_map[function] = tmp_list
        else:
          usa_functions_map[function] = [fvalue,]

    
    ind = np.arange(len(xa))
    plt.yscale('log')
    b1 = plt.bar(ind,ya, 0.25, color='red')
    plt.xticks(ind,xa, rotation=80)
    ff = plt.gcf()
    ff.subplots_adjust(bottom=0.35)
  
    plt.savefig(output+'/' + c + '_' + country +'.eps')


  # country combination
  xa = []
  ya = []

  plt = create_figure("Boxplot for functions in SA", "Functions", "Number of logs")

  tmp_data = []
  for f in f_map:
    tmp_data.append(sa_functions_map[f])
    xa.append(f)

  ind = np.arange(len(xa))
  plt.boxplot(tmp_data)
  plt.yscale('log')
  ff = plt.gcf()
  ff.subplots_adjust(bottom=0.35)

  plt.xticks(ind+1,xa, rotation=80)
  plt.savefig('./sa.eps')


  xa = []
  ya = []

  plt = create_figure("Boxplot for functions in USA", "Functions", "Number of logs")

  tmp_data = []
  for f in f_map:
    tmp_data.append(usa_functions_map[f])
    xa.append(f)
    
  ind = np.arange(len(xa))
  plt.boxplot(tmp_data)
  plt.yscale('log')
  ff = plt.gcf()
  ff.subplots_adjust(bottom=0.35)

  plt.xticks(ind+1,xa, rotation=80)
  plt.savefig('./usa.eps')


def load_pickled_data_skip_t(input_dir):
  pfile = open(input_dir + 'callers_map.p', 'rb')
  c_map = pickle.load(pfile)
  pfile.close()

  pfile = open(input_dir + 'functions_map.p', 'rb')
  f_map = pickle.load(pfile)
  pfile.close()

  pfile = open(input_dir + 'combination_map.p', 'rb')
  cf_map = pickle.load(pfile)
  pfile.close()

  return c_map, f_map, cf_map


def load_pickled_data(input_dir):
  t_lst = []
  pfile = open(input_dir + 'tuples_lst.p', 'rb')
  t_lst = pickle.load(pfile)
  pfile.close()

  pfile = open(input_dir + 'callers_map.p', 'rb')
  c_map = pickle.load(pfile)
  pfile.close()

  pfile = open(input_dir + 'functions_map.p', 'rb')
  f_map = pickle.load(pfile)
  pfile.close()

  pfile = open(input_dir + 'combination_map.p', 'rb')
  cf_map = pickle.load(pfile)
  pfile.close()

  return t_lst, c_map, f_map, cf_map


def time_analyze(p_data, output_dir, active_interval, num_logs, focus):

  # Unique routers
  router_to_times_map = {} 

  # Get pickled data
  fd = open(p_data, 'rb')
  t_map = pickle.load(fd)
  fd.close()

  ## Sort
  tkeys = sorted(t_map.keys())

  for k in tkeys:
    router_lst = t_map[k]
    for r in router_lst:
      if router_to_times_map.has_key(r) is True:
        router_to_times_map[r].append(datetime.strptime(str(k), "%Y%m%d"))
      else:
        router_to_times_map[r] = [datetime.strptime(str(k), "%Y%m%d"),]


  ## Get time flow, with missing dates
  start_t = datetime.strptime(str(tkeys[0]), "%Y%m%d")
  end_t = datetime.strptime(str(tkeys[-1]), "%Y%m%d")
  timeflow = [start_t,]
  st = start_t
  from datetime import timedelta
  while st < end_t:
    st = st + timedelta(days=1)
    timeflow.append(st)

  if focus == '0':
    active_routers_list = router_to_times_map.keys()
    print "Start date: ", start_t
    print "End date: ", end_t
    print '==========================================================='
    print 'Number of unique routers: ' + str(len(active_routers_list))
  
    print sorted(active_routers_list)

  elif focus == '1':
    active_routers_list = focus_list
    print "Start date: ", start_t
    print "End date: ", end_t
    print '==========================================================='
    print 'Number of unique routers: ' + str(len(active_routers_list))
  
    print sorted(active_routers_list)
 
  else:
    print 'unknonw focus value. exit'
    sys.exit(1)

  do_plot(active_routers_list, router_to_times_map, active_interval, num_logs, timeflow, output_dir,focus)

def do_plot(active_routers_list, router_to_times_map, active_interval, num_logs, timeflow, output_dir, focus):
  # active routers
  ya = {}
  sorted_rkeys = sorted(active_routers_list)
  for r in sorted_rkeys:
    t_list = router_to_times_map[r]
    if len(t_list) < num_logs:
      active_routers_list.remove(r)
    else:
      prev_date = t_list[0]
      for t in t_list:
        now_date = t
        tdelta = now_date - prev_date
        if tdelta.days > active_interval:
          if active_routers_list.count(r) != 0:
            active_routers_list.remove(r)
        prev_date = now_date

    ya[r] = []
    # Plot data
    for tt in timeflow:
      if t_list.count(tt) > 0:
        ya[r].append(1)
      else:
        ya[r].append(-1)

  print '==========================================================='
  print 'Number of active users: ' + str(len(active_routers_list))
  print sorted(active_routers_list)
   

  # Plot
  xa = timeflow
  colors = ['r-+','k-*','g-,','c-1','r-.']
  pl = []
  fig = plt.figure(dpi=700)
  ax = fig.add_subplot(111)

  for idx,r in enumerate(sorted_rkeys):
    real_ya = [i*(idx+1) for i in ya[r]]
#    pl.append( plt.plot(xa, [i*(idx+1) for i in ya[r]],  '%s' %(colors[idx])) )
    pl.append( plt.plot(xa, real_ya,  'r+',markersize=5) )
  
  #  majorind = np.arange(10,step=1)
  #  plt.xticks(majorind)
  ax.xaxis.grid(True, which='major')
  ax.yaxis.grid(True, which='major')
#  ax.set_yscale('log')
#  ax.set_xscale('log')
#  plt.ylim([1.0/1000.0,1000])
  
  ff = plt.gcf()
#  ax.set_xlim(1,50)
#
  ymajorind = np.arange(len(sorted_rkeys)+1,step=1)
  tmp = ['',] + [i for i in sorted_rkeys]
  plt.yticks(ymajorind,tmp, rotation=0, fontsize=6)
  plt.ylim(0,37)

#  ymajorind = np.arange(len(ya[sorted_rkeys[0]]),step=1)
  plt.xticks(rotation=45)

  ff.subplots_adjust(bottom=0.15)
  ff.subplots_adjust(left=0.30)
  plt.xlabel('Date', rotation=0)
  plt.ylabel('Routers', rotation=90)
#   plt.legend([p1[0],p2[0]], ['with events','without events'],  prop={'size':7})
#  plt.legend([pl[0][0],pl[1][0],pl[2][0],pl[3][0]], ['m=1','m=50','m=1000','baseline'],  prop={'size':7}, loc='upper center')

  fname = 'ui_usage_' + focus + '.eps'
  plt.savefig(output_dir + fname, dpi=700)



### main ###
def main():

  desc = ( 'Plot figures for ucap evalutaion' )
  usage = ( '%prog [options]\n'
            '(type %prog -h for details)' )
  op = OptionParser( description=desc, usage=usage )

  ### Options
  op.add_option( '--input', '-i', action="store", \
                 dest="input", help = "Input directory that has data." )
  op.add_option( '--output', '-o', action="store", \
                 dest="output", help = "Output directory for figures" )

  op.add_option( '--active_interval', '-t', action="store", \
                 dest="active_interval", help = "Usage intervals to be considered active" )

  op.add_option( '--nlogs_for_active', '-n', action="store", \
                 dest="nlogs_for_active", help = "Number of logs to be considered used" )

  op.add_option( '--focus', '-f', action="store", \
                 dest="focus", help = "Only plot focus routers (0 or 1)" )


  # Parsing and processing
  options, args = op.parse_args()
  args_check = sys.argv[1:]
  if len(args_check) != 10:
    print 'Something wrong with paramenters. Please check.'
    print op.print_help()
    sys.exit(1)

  ### Attach / if not there    
  input_dir = options.input
  output_dir = options.output
  if input_dir.endswith('/') is False:
    input_dir = input_dir + '/'
  output_dir = options.output
  if output_dir.endswith('/') is False:
    output_dir = output_dir + '/'

  # Check access
  if os.access(input_dir, os.R_OK) is False:
    print 'Cannot access input dir. Exit.'
    return
  if os.access(output_dir, os.R_OK) is False:
    print 'Cannot access output dir. Exit.'
    return

  # Set Active_interval and numlogs
  active_interval= int(options.active_interval)
  num_logs = int(options.nlogs_for_active)

#  # route id list
#  global sa_list
#  fd = open('./sa_routers.list','r')
#  sa_list = fd.readlines()
#  fd.close()
#
#  print sa_list
#

  ### Load pickled data
  indir = os.listdir(input_dir)
  if indir.count('timestamp_map.p') == 0:
    t_lst, c_map, f_map, cf_map = load_pickled_data(input_dir)
    make_lastlog_time(t_lst, input_dir)

  c_map, f_map, cf_map = load_pickled_data_skip_t(input_dir)

  # Analyze
  time_analyze(input_dir + 'timestamp_map.p', output_dir, active_interval, num_logs, options.focus)
  


  ### Plot
#  plot_work(t_lst, c_map, f_map, cf_map, output_dir)



###
if __name__ ==  '__main__':
    main()
###
