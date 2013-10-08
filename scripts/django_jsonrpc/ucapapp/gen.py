import pgsql as sql

unitTables = {'household':'households','user':'users','device':'devices'}
capTables = {'household':'household_caps_curr','user':'user_caps_curr',\
          'device':'device_caps_curr'}
userpointsTables = {'userpoints':'userpoints','baseline':'userpoints_baseline',\
                                       'points':'userpoints_points'}
default_user = 'default'

def get_config(key):
  sconf_str = './ucapapp/server.conf'
  config = open(sconf_str).readlines()
  for i in config:
    i = i.replace(" ","").replace('\n','').split("=")
    if i[0] == key:
      return i[1]
  return ''

def get_digest(hid=None,uid=None,did=None):
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
  res = sql.run_data_cmd(cmd)
  return res[0][0]

def get_group(arr,q=""):
    s = "("
    for i in arr:
        s = "%s%s%s%s,"%(s,q,i,q)
    s = s[:-1]
    s = "%s)"%(s)
    if s == ")":
      return "('000000000000')"
    else:
      return s
