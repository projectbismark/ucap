#!/usr/bin/python 

from gzip import GzipFile as gz
import pg as pgsql
import sys
import traceback
import os
import random as rnd
import socket, struct
import numpy as np
from gen import *

def sqlconn():
  sql_host = get_config('sql_host').strip()
  sql_user = get_config('sql_user').strip()
  sql_passwd = get_config('sql_passwd').strip()
  sql_db = get_config('sql_db').strip()

  try:
    conn = pgsql.connect(dbname=sql_db,host=sql_host,user=sql_user,passwd=sql_passwd)
  except:
    print "Could not connect to sql server"
    sys.exit()
  return conn

def run_insert_cmd(cmd,conn=None,prnt=0):
  if conn == None:
    conn = sqlconn()
  if prnt == 1:
    print cmd
  try:
    out = conn.query(cmd)
    if int(out) == 1:
      stat = (1,'SUCCESS')
    else:
      stat = (0,'ERROR')
  except:
    stat = (0,conn.error)
  #cursor.fetchall()
  return stat

def run_data_cmd(cmd,prnt=0):
  conn = sqlconn()
  res = ''
  if prnt == 1:
    print cmd
  try:
    res = conn.query(cmd)
  except:
    return (0,"ERROR") 
  result = res.getresult()
  #print 'in sql ',result
  return result 
