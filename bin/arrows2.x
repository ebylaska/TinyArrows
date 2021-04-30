#!/usr/bin/python

import subprocess,pymongo,random,getopt,sys,os,time,pickle

####################### mongoDB #############################
#uri = "mongodb://arrows:reaction@we17860.emsl.pnl.gov:27017"
with open("/srv/arrows/bin/.queue_nwchem",'r') as f: uri = f.readline().strip()
mongo_client       = pymongo.MongoClient(uri)
arrows_db          = mongo_client.Arrows
arrows_collection  = arrows_db.arrows_queue
dqueue_collection  = arrows_db.arrows_dqueue
####################### mongoDB #############################

############## machine parameters #########################
chemdb_fetch_reactions  = "/srv/arrows/bin/chemdb_fetch_reactions4 "
send_smtp               = "/srv/arrows/bin/send-smtp-arrows "
wrkdir                  = "/srv/arrows/Projects/Work"
lockfilename            = "/srv/arrows/Projects/Work/arrows2.lock"
############## machine parameters #########################

############################### Main Program  ####################################
usage = \
"""
arrows2 reactions program

  Usage: arrows2 -a -g id

  -a check all arrows jobs

"""

itid = -1
gtid = -1
checkall = True
opts, args = getopt.getopt(sys.argv[1:], "ahg:i:")
for o, a in opts:
  if '-i' in o:
     itid = eval(a)
  if '-g' in o:
     gtid = eval(a)
  if '-a' in o:
     checkall = True
  if o in ("-h","--help"):
    print usage
    exit()


### lockfile ###
if os.path.isfile(lockfilename): 
   print "i am locked lockfilename:", lockfilename
   exit()
with open(lockfilename,'w') as lfile: lfile.write("iamlocked\n")



aname = "arrows2-%d" % random.randint(0,9999999)
aname1 = aname+'.txt'
aname2 = aname+'.html'
tsg = ''

dqueue = []
if (itid!=-1):
   query = {'queue_number': itid}
elif (gtid>-1):
   query = {'queue_number': {'$gt': gtid}}
else:
   query = {}
sort = [('queue_number',pymongo.ASCENDING)]
try:
   arrows_q = arrows_collection.find(query,no_cursor_timeout=True)
except:
   arrows_q = []

try:
   for job in arrows_q.batch_size(2):

      veryold = False
      if (job.has_key('submit_gm_time')):
         gt = pickle.loads(job['submit_gm_time'])
         veryold = (((time.gmtime()[1] - gt[1])%12) > 1)

      count        = job['count']
      reactions    = job['reactions']
      emailsubject = job['emailsubject']
      emailfrom    = job['emailfrom']
      emailcc      = job['emailcc']
      queue_number = job['queue_number']
      print "queue_number=",queue_number
      try:
         qq = arrows_collection.update({'queue_number':queue_number},{'$inc':{'count':1}})
      except:
         print "arrows2: Failed to update count for job[queue_number=%d] in arrows colection." % queue_number
      #submitmissingesmiles = "submitmissingesmiles" in reactions.lower()
      submitmissingesmiles = True
      print "queue_number =",queue_number," count=",count," submitmissingesmiles=",submitmissingesmiles

      ofile = open(wrkdir + "/" + aname1,'w')
      ofile.write(reactions)
      ofile.write("\nemailfrom: " + emailfrom + " :emailfrom\n")
      ofile.write("\nemailcc: " + emailcc + " :emailcc\n")
      ofile.close()

      cmd = chemdb_fetch_reactions + wrkdir + '/' + aname1 + ' ' + wrkdir + '/' + aname2

      try:
         print "running cmd:",cmd
         tsg += "running cmd:" + cmd + "\n"
         result = subprocess.check_output(cmd,shell=True)
         print
         print result
         print
         tsg += "\n" + result + "\n"
         success = "All requests to Arrows were successful." in result
      except:
         success = False

      success = success or (count>120)
      ### email results if success or count > 120 ###
      if (success):
         if (count>120):
            subjct = "days>30: Arrows Re: " + emailsubject
         else:
            subjct = "Arrows Re: " + emailsubject
         cmd2 = send_smtp + " -m " +'\"' + emailfrom + emailcc + '\"' + ' -j \"' + subjct + '\" -t ' + wrkdir + '/' + aname2
         print "cmd2= " + cmd2
         tsg += "running cmd2:" + cmd2 + "\n"
         try:
            result2 = subprocess.check_output(cmd2,shell=True)
         except:
            result2 = "arrows2: failed to send email."
         print
         print result2
         tsg += "\n" + result2 + "\n"

         #if (toolongcount > toolongcountmax): toolong = True
         #toolongcount += 1

      ### remove item from arrows_queue if success or not submitmissingesmiles or veryold ***
      if success or (not submitmissingesmiles) or veryold:
         try:
            dqueue_collection.insert(job)
         except:
            print "arrows2: Failed to insert job to nwchem_dqueue."
         try:
            arrows_collection.remove({'queue_number':job['queue_number']})
         except:
            print "arrows2: Failed to remove job from nwchem_queue."

except:
   print "arrows2: Failed to complete arrows_q  for loop."


##remove dqueue list from arrows_collection
#if (len(dqueue) > 0):
#   for i in range(len(dqueue)):
#      try:
#         arrows_collection.remove({'queue_number':dqueue[i]})
#      except:
#         print "arrows2: Failed to remove job from nwchem_queue."
   

### write parsed output ###
oofile = open(wrkdir + "/arrows2.parse","w")
oofile.write(tsg)
oofile.close()


### remove arrows2 files ####
try:
   os.unlink(wrkdir + "/" + aname1)
except:
   print "arrows2: failed to remove " + wrkdir + "/" + aname1


try:
   os.unlink(wrkdir + "/" + aname2)
except:
   print "arrows2: failed to remove " + wrkdir + "/" +  aname2


### remove lockfilename ###
try:
   os.unlink(lockfilename)
except:
   print "arrows2: failed to remove " + lockfilename


print "FINISHED RUNNING arrows2.x"
