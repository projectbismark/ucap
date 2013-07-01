
import pickle
import sys

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from numpy.random import normal
import pylab
import numpy as np


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


def load_pickled_data():
  t_lst = []
#  pfile = open('./tuples_lst.p', 'rb')
#  t_lst = pickle.load(pfile)
#  pfile.close()

  pfile = open('./callers_map.p', 'rb')
  c_map = pickle.load(pfile)
  pfile.close()

  pfile = open('./functions_map.p', 'rb')
  f_map = pickle.load(pfile)
  pfile.close()

  pfile = open('./combination_map.p', 'rb')
  cf_map = pickle.load(pfile)
  pfile.close()

  return t_lst, c_map, f_map, cf_map


### main ###
def main():

  args = sys.argv[1:]
  if len(args) is not 1:
    print '\n##############################################################'
    print 'usage: python  analysis_and_plots.py <output dir>'
    print '###############################################################\n'
    sys.exit(1)

  output_dir = args[0]

  # route id list
  global sa_list
  fd = open('./sa_routers.list','r')
  sa_list = fd.readlines()
  fd.close()

  print sa_list

  t_lst, c_map, f_map, cf_map = load_pickled_data()
  plot_work(t_lst, c_map, f_map, cf_map, output_dir)



###
if __name__ ==  '__main__':
    main()
###
