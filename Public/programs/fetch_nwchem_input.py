#!/usr/bin/python
import os,sys,subprocess,urllib2,requests,getopt

arrows_queue_url       = 'https://arrows.pnnl.gov/api/queue/'
arrows_queue_fetch_url = 'https://arrows.pnnl.gov/api/queue_fetch/'


############################# main program ###################################
usage = \
"""
fetch_nwchem_input

  Usage: fetch_nwchem_input -q -e queue_entry -m machinetype -h 

  -h help

"""

print
print "#fetch_nwchem_input - version 1.0"
print

showq       = True
queue_entry = -1
machinetype = ''
opts, args = getopt.getopt(sys.argv[1:], "e:m:qh")
for o, a in opts:
  if '-q' in o:
     showq       = True
  if '-e' in o:
     queue_entry = eval(a)
     showq       = False
  if '-m' in o:
     machinetype = a
     showq       = False

  if o in ("-h","--help"):
    print usage
    exit()


if showq:
   try:
      rr = requests.get(arrows_queue_url)
      print rr.text.split('#chemdb_queue - version 1.0')[1].split('</pre>')[0].strip()
   except:
      print " - API Failed"

if machinetype!='':
   try:
      rr = requests.get(arrows_queue_url)
      fmax = 999999
      qmax = -1
      for ln in rr.text.split('\n'):
         if machinetype in ln:
            ss = ln.split()
            f = eval(ss[2])
            q = eval(ss[0])
            if f<fmax:
               fmax = f
               qmax = q
      queue_entry = qmax
   except:
      print " - API Failed"

if (queue_entry!=-1):
   try:
      rr = requests.get(arrows_queue_fetch_url + "%d" % queue_entry)
      print rr.text.split('#chemdb_queue - version 1.0')[1].split('</pre>')[0].strip()
   except:
      print " - API Failed"

