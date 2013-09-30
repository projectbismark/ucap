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
import dpkt
from matplotlib.patches import ConnectionPatch
import struct
from socket import *

mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif', 'sans-serif': ['Times'], 'size': 9})
mpl.rc('figure', figsize=(3.33, 2.06))
mpl.rc('axes', linewidth=0.5)
mpl.rc('patch', linewidth=0.5)
mpl.rc('lines', linewidth=0.5)
mpl.rc('grid', linewidth=0.25)


sa_list = []

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









def lastlog_time(t_lst, c_map, f_map, cf_map):
#####
# Table "public.function_call_log"
#    Column   |            Type             | Modifiers
# ------------+-----------------------------+-----------
#  caller     | id_t                        |
#  name       | fname_t                     |
#  parameters | fparam_t                    |
#  calltime   | timestamp without time zone (2013-04-02 19:01:34) |
#####
  timestamp_to_routers_map = {}

  for t in t_lst:
#    ts_str = t[3]
#    ts = datetime.strptime(ts_str, "%Y-%M-d %H:%M:%S")
       
    ts_str = t[3]
    date_int = int(ts_str[:11].strip('-'))
    if timestamp_to_routers_map.has_key(date_int) is True:
      timestamp_to_routers_map[date_int].append(t[0])
    else:
      timestamp_to_routers_map[date_int] = [t[0],]

  tkeys = sorted(timestamp_to_routers_map.keys())
  for t in tkeys:
    print t
    print timestamp_to_routers_mapt[t]

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

  ### Check option     
  options, args = op.parse_args()
  if options.input is None or options.output is None:
    print 'Wrong number of arguments. exit'
    return
    
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

#  # route id list
#  global sa_list
#  fd = open('./sa_routers.list','r')
#  sa_list = fd.readlines()
#  fd.close()
#
#  print sa_list
#

  ### Load pickled data
  t_lst, c_map, f_map, cf_map = load_pickled_data(input_dir)

  ### Analyze
  lastlog_time(t_lst, c_map, f_map, cf_map)

  ### Plot
#  plot_work(t_lst, c_map, f_map, cf_map, output_dir)



###
if __name__ ==  '__main__':
    main()
###
