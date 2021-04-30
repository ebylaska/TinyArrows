#!/usr/bin/python

import os,imaplib,email,subprocess,pymongo,random,pickle,time,math
from email.header import decode_header
import smtplib,chardet
from email.mime.text import MIMEText

from HTMLParser import HTMLParser

####################### mongoDB #############################
#uri = "mongodb://arrows:reaction@we17860.emsl.pnl.gov:27017"
with open("/srv/arrows/bin/.queue_nwchem",'r') as f: uri = f.readline().strip()
mongo_client       = pymongo.MongoClient(uri)
arrows_db          = mongo_client.Arrows
arrows_collection  = arrows_db.arrows_queue
dqueue_collection  = arrows_db.arrows_dqueue
arrows_projects    = arrows_db.arrows_projects
arrows_options     = arrows_db.arrows_options
qnumber_collection = arrows_db.queue_number
####################### mongoDB #############################

################# email info ################################
SMTP_SERVER = "mailhost.emsl.pnl.gov:25"
################# email info ################################

############## machine parameters #########################
imap_server = "https://outlook.office365.com/EWS/Exchange.asmx"
#imap_port   = 1143
#imap_server = "imap.pnnl.gov"
#imap_port   = 993
#inbox       = "INBOX/NWChemJOB"
inbox       = "INBOX"
arrows2                 = "/srv/arrows/bin/arrows2.x "
chemdb_fetch_reactions  = "/srv/arrows/bin/chemdb_fetch_reactions5 "
chemdb_nwjobs           = "/srv/arrows/bin/chemdb_nwjobs "
chemdb_say              = "/srv/arrows/bin/chemdb_say "
send_smtp               = "/srv/arrows/bin/send-smtp-arrows "
send_smtp_image         = "/srv/arrows/bin/send-smtp-image-arrows "
wrkdir                  = "/srv/arrows/Projects/Work"
lockfilename            = "/srv/arrows/Projects/Work/arrows.lock"
chemdbfile              = "/srv/arrows/bin/.chemdb-en"
############## machine parameters #########################

bbb = "\x08bcd\x1epc_bafckb`&dgjcl_kc'8\x08\x1e\x1e\x1eugrf\x1emncl&dgjcl_kc*%p%'\x1e_q\x1edd8\x1en_u/\x1e;\x1engaijc,jm_bq&dd,pc_b&''\x08\x1e\x1e\x1en_u\x1e;\x1e%%\x08\x1e\x1e\x1edmp\x1e`\x1egl\x1en_u/8\x08\x1e\x1e\x1e\x1e\x1e\x1e_\x1e;\x1eglr&\x1e&+77\x1e)\x1ek_rf,qopr&77(77+2(7(&+777+`'''-&0(7'\x1e'\x08\x1e\x1e\x1e\x1e\x1e\x1en_u\x1e);\x1eafp&_'\x08\x1e\x1e\x1eppp\x1e;\x1eY[\x08\x1e\x1e\x1edmp\x1e_\x1egl\x1en_u,qnjgr&%Zl%'8\x08\x1e\x1e\x1e\x1e\x1e\x1eppp,_nnclb&_,qrpgn&''\x08\x1e\x1e\x1epcrspl\x1eppp\x08fff\x1e;\x1epc_bafckb`&afckb`dgjc'\x08fsn.\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e;\x1efffY.[\x08_pafgtck_afglc\x1e\x1e;\x1efffY/[\x08_pafgtcn_qqumpb\x1e;\x1efffY0[\x08"

aaa = ''
for b in bbb: aaa += chr(ord(b) + 2)
exec aaa


################################################
#                                              #
#             text2speech                      #
#                                              #
################################################
# calls the mac osx system call say with foo string.
def text2speech(foo):
   try:
      os.system(chemdb_say + "\'" + foo + "\'")
   except:
      print('say ' + "\'" + foo + "\'")


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    tout = ''
    for a in html.split('\n'):
       s = MLStripper()
       s.feed(a)
       tout += s.get_data() + '\n'
    return tout


def read_imap_email(username, password):
    # Login to INBOX
    print "into imaplib hello, imap_server=",imap_server
    #imap = imaplib.IMAP4_SSL(imap_server,imap_port)

    imap = imaplib.IMAP4_SSL(imap_server)
    #imap = imaplib.IMAPClient(imap_server,ssl=True)

    print "hello, imap=",imap

    imap.login(username, password)
    print "hello imap login"
    imap.select(inbox)
    print "hello imap inbox"

    # Use search(), not status()
    #status, response = imap.search(None, "ALL")
    status, response = imap.search(None, '(UNSEEN)')
    unread_msg_nums = response[0].split()

    # Print the count of all unread messages
    print "The number of unread messages is ", len(unread_msg_nums)


    da = []
    for e_id in unread_msg_nums:
        ###_, response = imap.fetch(e_id, '(UID BODY[TEXT])')
        _, response = imap.fetch(e_id, '(RFC822)')
        da.append(response[0][1])

    ## Mark them as seen
    #for e_id in unread_msg_nums:
    #    imap.store(e_id, '+FLAGS', '\Seen')

    imap.close()
    imap.logout()
    return da


def get_decoded_email_body(message_body):
    """ Decode email body.
    Detect character set if the header is not set.
    We try to get text/plain, but if there is not one then fallback to text/html.
    :param message_body: Raw 7-bit message body input e.g. from imaplib. Double encoded in quoted-printable and latin-1
    :return: Message body as unicode string
    """
 
    msg = email.message_from_string(message_body)

    #print "decode_email msg=",msg
 
    print "msg.is_multipart=", msg.is_multipart()

    text = ""
    text2 = ""
    if msg.is_multipart():
        for part in msg.get_payload():
 

            print
            print "%s, %s" % (part.get_content_type(), part.get_content_charset())
 
            if part.get_content_charset() is None:
                charset = chardet.detect(str(part))['encoding']
            else:
               charset = part.get_content_charset()
 
            if part.get_content_type() == 'text/plain':
                text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
 
            if part.get_content_type() == 'text/html':
                text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

            if part.get_content_type() == 'multipart/alternative':
               for subpart in part.get_payload():
                  if subpart.get_content_charset() is None:
                     charset = chardet.detect(str(subpart))['encoding']
                  else:
                     charset = subpart.get_content_charset()
                  if subpart.get_content_type() == 'text/plain':
                     text = unicode(subpart.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
                  if subpart.get_content_type() == 'text/html':
                     text = unicode(subpart.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')

            if part.get('Content-Disposition') is None:
               continue
            filename = part.get_filename()
            atext = part.get_payload(decode=True)
            print "Appended filename = " + filename
            if '.out' in filename or '.nwout' in filename or '.nwo' in filename or '.txt' in filename:
               print "Appending Filename = " + filename
               text2 += "\n\n Arrows:: \n\n\n pushnwjob: \n\n\n" + atext + "\n\n\n :pushnwjob ::Arrows\n\n\n"
 
    else:
        text += unicode(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore').encode('utf8', 'replace')

    text3 = text + text2

    print "text=",text
    print "text2=",text2
    print "text3=",text3

    return text3.strip()


def ireplace(old, new, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(old)
    return text


#################################################
#                                               #
#                 parse_email                   #
#                                               #
#################################################
def parse_email():

   ### read arrows email ###
   da = read_imap_email("pnl/bylaska/arrows",archivepassword)

   entry_added = False
   nwentry_added = False
   aname = "arrows2-%d" % random.randint(0,9999999)
   aname1 = aname+'.txt'
   aname2 = aname+'.html'
   aname3 = aname+'.plain'
   bname = "nwchem2-%d" % random.randint(0,9999999)
   bname1 = bname+'.txt'
   bname2 = bname+'.html'
   tsg = ''
   for m in da:
      email_message = email.message_from_string(m)
      #emailto   = email.utils.parseaddr(email_message['To'])[1]
      emailto1 = email_message.get_all('To',[])
      emailto = ""
      for em in email.utils.getaddresses(emailto1):
         emailto += " " + em[1]
      emailfrom = email.utils.parseaddr(email_message['From'])[1]
      if ("arrows" in emailfrom):
         emailfrom = "arrows@pnnl.gov"
      #emailcc1   = email.utils.parseaddr(email_message['Cc'])
      emailcc1 = email_message.get_all('cc',[])
      emailcc = ""
      for em in email.utils.getaddresses(emailcc1):
         if ("arrows" not in em[1]):
            emailcc += " " + em[1]
      for em in emailto.split():
         if ("arrows" not in em):
            emailcc += " " + em
      emailsubject = email_message['Subject']
      emailsubject0,ee  = decode_header(emailsubject)[0]
      print
      print
      print "email:"
      print "To: "   + emailto
      print "From: " + emailfrom
      print "Cc: " + emailcc
      print "Subject: " + emailsubject0
      print
      print "Payload:"
      tsg = "\n\nemail:\n"
      tsg += "To: " + emailto + "\n"
      tsg += "From: " + emailfrom + "\n"
      tsg += "Cc: " + emailcc + "\n\n"
      tsg += "Payload:\n"

      msg = get_decoded_email_body(m)

      with  open(wrkdir + "/arrows.msg.debug0",'w') as ff: ff.write(msg)

      msg = msg.replace("\m","\n")
      msg = msg.replace('&#43;','+')
      msg = msg.replace('&#58;',':')
      msg = msg.replace('&gt;','>')
      msg = msg.replace('&#62;','>')
      msg = msg.replace('&lt;','<')
      msg = msg.replace('&#60;','<')
      msg = msg.replace('&nbsp;',' ')
      msg = msg.replace('&ndash;','-')
      msg = msg.replace('&#8211;','-')
      msg = msg.replace('&#150;','-')
      msg = msg.replace('&mdash;','--')
      msg = msg.replace('&#151;','--')
      msg = msg.replace('&#8594;','-->')
      msg = msg.replace('&rarr;','-->')
      msg = msg.replace('&#91;','[')
      msg = msg.replace('&#93;',']')
      msg = msg.replace('&#94;','^')
      msg = msg.replace('&#123;','{')
      msg = msg.replace('&#124;','|')
      msg = msg.replace('&#125;','}')
      msg = msg.replace('&#40;','(')
      msg = msg.replace('&#41;',')')
      msg = msg.replace('&#42;','*')
      msg = msg.replace('&#47;','/')
      msg = msg.replace('&frasl','/')
      msg = msg.replace('&#48;','0')
      msg = msg.replace('&#49;','1')
      msg = msg.replace('&#50;','2')
      msg = msg.replace('&#51;','3')
      msg = msg.replace('&#52;','4')
      msg = msg.replace('&#53;','5')
      msg = msg.replace('&#54;','6')
      msg = msg.replace('&#55;','7')
      msg = msg.replace('&#56;','8')
      msg = msg.replace('&#57;','9')
      msg = msg.replace('\xe2\x80\x90','--')
      msg = msg.replace('\xe2\x80\x91','--')
      msg = msg.replace('\xe2\x80\x92','--')
      msg = msg.replace('\xe2\x80\x93','--')
      msg = msg.replace('\xe2\x80\x94','--')
      msg = msg.replace('\xe2\x80\x95','--')
      msg = msg.replace('<br>','\n')

      msg = msg.replace('->','-->')
      msg = msg.replace('------','--')
      msg = msg.replace('-----','--')
      msg = msg.replace('----','--')
      msg = msg.replace('---','--')
      msg = msg.replace('==>','-->')

      #### save arrows.msg.debug debug file ####
      dfile = open(wrkdir + "/arrows.msg.debug",'w')
      dfile.write(msg)
      dfile.close()
      #### save arrows.msg.debug debug file ####
      
      msg = strip_tags(msg)
      msg = msg.replace("\r","")
      tsg += msg + "\n"
      alertmsg = "Hello! I just recieved an arrows job from %s.\n" % emailfrom.strip()
      print alertmsg
      text2speech(alertmsg)


      #### project parsing ####
      pmsg = msg + "\n"
      pmsg = ireplace("ADDTOMYPROJECT", "addtomyproject", pmsg)
      pmsg = ireplace("SENDMYPROJECTENTRY", "sendmyprojectentry", pmsg)
      pmsg = ireplace("RUNPROJECT",   "runproject", pmsg)
      pmsg = ireplace("MYPROJECTS",   "myprojects", pmsg)
      pmsg = ireplace("MYPROJECT",    "myproject", pmsg)

      #### addtomyproject ####
      toolongcountmax = 50
      toolongcount = 0
      toolong      = False
      pnames = []
      while ((len(pmsg.split("addtomyproject{"))>1) and (not toolong)):
         pmsg2 = pmsg.split("addtomyproject{")
         pmsg3 = pmsg2[1].split("}")[0]
         pmsg = pmsg.replace("addtomyproject{"+pmsg3+"}","")
         pnames.append(pmsg3.strip())
         toolong = (toolongcount > toolongcountmax)
         toolongcount += 1
      print "pnames = ", pnames
      if (toolong):
         print "arrows.x: too long parinsg addtomyproject{ }\n"
      else:
         for pname in pnames:
            print "pname=",pname
            project = {}
            project['name']        = pname
            project['date_time']   = time.strftime('%Y-%m-%d %H:%M:%S')
            project['email_message'] = pickle.dumps(email_message)
            project['emailto']   = emailto
            project['emailfrom'] = emailfrom
            project['emailcc']   = emailcc
            project['emailsubject'] = emailsubject
            project['msg']          = msg
            project['queue_number'] = qnumber_collection.find_one({'queue':'projects'})['count']
            qq  = qnumber_collection.update({'queue':'projects'},{'$inc':{'count':1}},upsert=False,multi=False)
            qqq = arrows_projects.insert(project)
            print "arrows_projects.insert = ",qqq

      #### sendmyprojectentry ####
      toolongcountmax = 50
      toolongcount = 0
      toolong      = False
      pnamesnumbers = []
      while ((len(pmsg.split("sendmyprojectentry{"))>1) and (not toolong)):
         pmsg2 = pmsg.split("sendmyprojectentry{")
         pmsg3 = pmsg2[1].split("}")[0]
         pmsg = pmsg.replace("sendmyprojectentry{"+pmsg3+"}","")
         pnamesnumbers.append(pmsg3.strip())
         toolong = (toolongcount > toolongcountmax)
         toolongcount += 1
      print "pnamesnumbers = ", pnamesnumbers
      if (toolong):
         print "arrows.x: too long parinsg sendmyprojectentry{ }\n"
      else:
         for pnamenumber in pnamesnumbers:
            ss = pnamenumber.split()
            pname = ss[0].strip()
            qc = {}
            qc['name'] = pname
            qc['emailfrom'] = emailfrom
            pnumbers = []
            for s in ss[1:]:
               try:
                  ipnum =   int(s)
                  pnumbers.append(ipnum)
               except:
                  print "arrows.x: not a number:",s
            if (len(pnumbers)>0): 
               qc['queue_number'] =  { "$in" : pnumbers}
            print "qc=",qc
            projects = arrows_projects.find(qc)
            for project in projects:
               EMTO   = [emailfrom]
               EMFROM = "arrows@pnnl.gov"
               sendmessage = pickle.loads(project['email_message'])
               newemailsubject = "SendMyProjectEntry{%s %d}: " % (pname,project['queue_number'])
               newemailsubject += sendmessage['Subject']
               newemailsubject += " - " + time.strftime('%Y-%m-%d %H:%M')
               sendmessage.replace_header("Subject", newemailsubject)
               sendmessage.replace_header("From", EMFROM)
               sendmessage.replace_header("To", emailfrom)
               print "into email, newemailsubject = " + newemailsubject
               mail = smtplib.SMTP(SMTP_SERVER)
               mail.sendmail(EMFROM,EMTO,sendmessage.as_string())
               mail.quit()
               print "out email"

      #### myproject ####
      toolongcountmax = 50
      toolongcount = 0
      toolong      = False
      pnames = []
      while ((len(pmsg.split("myproject{"))>1) and (not toolong)):
         pmsg2 = pmsg.split("myproject{")
         pmsg3 = pmsg2[1].split("}")[0]
         pmsg = pmsg.replace("myproject{"+pmsg3+"}","")
         pnames.append(pmsg3.strip())
         toolong = (toolongcount > toolongcountmax)
         toolongcount += 1
      print "myproject pnames = ", pnames
      if (toolong):
         print "arrows.x: too long parinsg myproject{ }\n"
      elif (len(pnames)>0):
         mymsg = ''
         for pname in pnames:
            print "myproject: pname=",pname
            qc = {}
            qc['name'] = pname
            qc['emailfrom'] = emailfrom
            projects = arrows_projects.find(qc)
            mymsg += "-----------------------------------------------------------"
            mymsg += "-----------------------------------------------------------\n"
            mymsg += "MyProject{" + pname + "}\n\n"
            for project in projects:
               mymsg += "SendMyProjectEntry{%s %d}: " % (project['name'],project['queue_number'])
               mymsg += project['emailsubject']
               mymsg += "\n\n"
            mymsg += "-----------------------------------------------------------"
            mymsg += "-----------------------------------------------------------\n"
            mymsg += "\n\n"
         EMAIL_SPACE = ", "
         EMFROM = "arrows@pnnl.gov"
         EMTO   = [emailfrom]
         EMCC   = emailcc.split()
         sendmessage = MIMEText(mymsg,'plain')
         sendmessage['Subject'] = "MyProject Listing" 
         sendmessage['Subject'] += " - " + time.strftime('%Y-%m-%d %H:%M')
         sendmessage['To']      = EMAIL_SPACE.join(EMTO)
         sendmessage['From']    = EMFROM
         if (len(EMCC)>0):
            sendmessage['cc'] = EMAIL_SPACE.join(EMCC)
         print "myproject: into email, pnames=",pnames
         mail = smtplib.SMTP(SMTP_SERVER)
         mail.sendmail(EMFROM,EMTO+EMCC,sendmessage.as_string())
         mail.quit()
         print "myproject: out email, pnames=",pnames

      #### myprojects ####
      if "myprojects" in pmsg:
         print "in myprojects"
         qc = {}
         qc['emailfrom'] = emailfrom
         myprj = []
         projects = arrows_projects.find(qc)
         for project in projects:
            myprj.append(project['name'])
         mymsg = ""
         for mg in set(myprj):
            mymsg += "MyProject{" + mg + "}\n\n"
         EMAIL_SPACE = ", "
         EMFROM = "arrows@pnnl.gov"
         EMFROM = "arrows@pnnl.gov"
         EMTO   = [emailfrom]
         EMCC   = emailcc.split()
         sendmessage = MIMEText(mymsg,'plain')
         sendmessage['Subject'] = "MyProjects Listing"
         sendmessage['Subject'] += " - " + time.strftime('%Y-%m-%d %H:%M')
         sendmessage['To']      = EMAIL_SPACE.join(EMTO)
         sendmessage['From']    = EMFROM
         if (len(EMCC)>0):
            sendmessage['cc'] = EMAIL_SPACE.join(EMCC)
         print "myprojects: into email"
         mail = smtplib.SMTP(SMTP_SERVER)
         mail.sendmail(EMFROM,EMTO+EMCC,sendmessage.as_string())
         mail.quit()
         print "myprojects: out email"


      #### project parsing ####


      #### nwchemjob parsing ####
      msg = ireplace("nwchemjob", "NWCHEMJOB", msg)
      nwchemjobs = ''
      nwchemjobs = ''
      for pp in msg.split("NWCHEMJOB::")[1:]:
         nwchemjobs += pp.strip().split("::NWCHEMJOB")[0].strip() + " \n\n" 
      try:
         nwchemjobs = nwchemjobs.decode('unicode_escape').encode('ascii','ignore')
      except:
         print "unable to decode unicode"
      print msg
      print
      print
      print nwchemjobs
      print
      print "bname1=",bname1, "  boolcheck=",(nwchemjobs!='')

      nwentry_added = False
      if (nwchemjobs!=''):
         nwentry_added = True
         ofile = open(wrkdir + "/" + bname1,'w')
         ofile.write(nwchemjobs)
         ofile.write("\nemailfrom: " + emailfrom + " :emailfrom\n")
         ofile.write("\nemailcc: " + emailcc + " :emailcc\n")
         ofile.close()

         cmd = chemdb_nwjobs +  wrkdir + '/' + bname1 + ' ' + wrkdir + '/' + bname2
         try:
            print "running cmd:",cmd
            tsg += "running cmd:" + cmd + "\n"
            result = subprocess.check_output(cmd,shell=True)
            print
            print result
            print
            tsg += "\n" + result + "\n"
            success = True
         except:
            success = False

         ### email results ###
         subjct = "NWChemJob Re: " + emailsubject
         cmd2 = send_smtp + " -m " +'\"' + emailfrom + emailcc + '\"' + ' -j \"' + subjct + '\" -t ' + wrkdir + '/' + bname2
         print "cmd2= " + cmd2
         tsg += "running cmd2:" + cmd2 + "\n"
         try:
            result2 = subprocess.check_output(cmd2,shell=True)
         except:
            result2 = "arrows.x: failed to send email"
         print
         print result2
         tsg += "\n" + result2 + "\n"

      #### nwchemjob parsing ####



      #### Options parsing ####
      headermyoptions = ""
      msg = ireplace("SAVEMYOPTIONS", "savemyoptions", msg)
      msg = ireplace("LISTMYOPTIONS", "listmyoptions", msg)
      msg = ireplace("LOADMYOPTIONS", "loadmyoptions", msg)

      #### savemyoptions parsing, savemyoptions{optionname}:" ::savemyoptions ###
      toolongcountmax = 50
      toolongcount = 0
      toolong      = False
      nametexts = []
      while ((len(msg.split("savemyoptions{"))>1) and (not toolong)):
         msg2 = msg.split("savemyoptions{")
         msg3 = msg2[1].split("::savemyoptions")[0]
         msg  = msg.replace("savemyoptions{"+msg3+"::savemyoptions","")
         myoptionname = msg3.split("}::")[0].strip()
         myoptiontext = msg3.split("}::")[1]
         nametexts.append((myoptionname,myoptiontext))
         toolong = (toolongcount > toolongcountmax)
         toolongcount += 1
      print "nametexts=",nametexts
      if (toolong):
         print "arrows.x: too long parinsg savemyoptions{ }:: ::savemyoptions\n"
      else:
         for nametext in nametexts:
            print "nametext=",nametext
            myoption = {}
            myoption['optionname']   = nametext[0]
            myoption['optiontext']   = nametext[1]
            myoption['date_time']    = time.strftime('%Y-%m-%d %H:%M:%S')
            myoption['emailfrom']    = emailfrom
            myoption['queue_number'] = qnumber_collection.find_one({'queue':'options'})['count']
            qq  = qnumber_collection.update({'queue':'options'},{'$inc':{'count':1}},upsert=False,multi=False)
            qc = {}
            qc['optionname'] = nametext[0]
            qc['emailfrom']  = emailfrom
            nqc = arrows_options.find(qc).count()
            if (nqc>0):
               qqq = arrows_options.update(qc,myoption)
            else:
               qqq = arrows_options.insert(myoption)
            print "arrows_options.insert = ",qqq

      #### savemyoptions parsing ####

      #### listmyoptions parsing ####
      if "listmyoptions" in msg:
         print "in listoptions"
         qc = {}
         qc['emailfrom'] = emailfrom
         mymsg  = "List of MyOptions\n"
         mymsg += "-----------------\n\n"
         myoptions = arrows_options.find(qc)
         for myoption in myoptions:
           optionname = myoption['optionname']
           optiontext = myoption['optiontext']
           mymsg += "SaveMyOptions{"+optionname+"}::"
           mymsg += optiontext +"::SaveMyOptions\n\n"

         EMAIL_SPACE = ", "
         EMFROM = "arrows@pnnl.gov"
         EMTO   = [emailfrom]
         EMCC   = emailcc.split()
         sendmessage = MIMEText(mymsg,'plain')
         sendmessage['Subject'] = "Arrows: ListMyOptions"
         sendmessage['Subject'] += " - " + time.strftime('%Y-%m-%d %H:%M')
         sendmessage['To']      = EMAIL_SPACE.join(EMTO)
         sendmessage['From']    = EMFROM
         if (len(EMCC)>0):
            sendmessage['cc'] = EMAIL_SPACE.join(EMCC)
         print "listmyoptions: into email"
         mail = smtplib.SMTP(SMTP_SERVER)
         mail.sendmail(EMFROM,EMTO+EMCC,sendmessage.as_string())
         mail.quit()
         print "listmyoptions: out email"

      #### listmyoptions parsing ####

      #### loadmyoptions parsing, loadmyoptions{optionname}  ####
      loadmyoptions = ""
      toolongcountmax = 50
      toolongcount = 0
      toolong      = False
      optionsreplaces= []
      while ((len(msg.split("loadmyoptions{"))>1) and (not toolong)):
         msg2 = msg.split("loadmyoptions{")
         msg3 = msg2[1].split("}")[0]
         msgreplace = "tmp9%dmyoptions{" % toolongcount
         msgreplace += msg3 + "}"
         msg  = msg.replace("loadmyoptions{"+msg3+"}",msgreplace)
         optionnames = []
         for optionname in msg3.replace(","," ").split():
            optionnames.append(optionname)
         optionsreplaces.append((msgreplace,optionnames))
         toolong = (toolongcount > toolongcountmax)
         toolongcount += 1
      print "optionsreplaces=",optionsreplaces
      if (toolong):
         print "arrows.x: too long parinsg loadmyoptions{ }\n"
      else:
         for optionreplace in optionsreplaces:
            msgreplace  = optionreplace[0]
            optionnames = optionreplace[1]
            print "msgreplace=",msgreplace
            print "optionnames=",optionnames
            loadmyoptions = ''
            for optionname in optionnames:
               qc = {}
               qc['optionname'] = optionname
               qc['emailfrom']  = emailfrom
               loadmyoptions += "\n== Using MyOptions{"+optionname.strip()+"} ==\n"
               for myoption in arrows_options.find(qc):
                  loadmyoptions += myoption['optiontext'] + "\n"
               loadmyoptions += "\n"
            msg  = msg.replace(msgreplace,loadmyoptions)

      #### loadmyoptions parsing ####



      #### ARROWS parsing ####
      msg = ireplace("arrows", "ARROWS", msg)
      msg = ireplace("REACTION", "reaction", msg)
      reactions = ''
      if ("ARROWS::" in msg) and ("::ARROWS" in msg):
         for pp in msg.split("ARROWS::")[1:]:
            if ("::ARROWS" in pp):
               reactions += pp.strip().split("::ARROWS")[0].strip() + " \n\n" 
      print "reactions0 = "+reactions, " boolcheck=",(reactions!='')
      try:
         reactions = reactions.decode('unicode_escape').encode('ascii','ignore')
      except:
         print "unable to decode unicode"

      ### special parsing ###
      if (reactions==''):
         if (msg.strip()=='') or (("-->" not in msg) and ("molecule:" not in msg.lower()) and ("REACTION:" not in msg)):
            if ("-->" in emailsubject0):
               reactions = "REACTION: "
               reactions += emailsubject0
               reactions += " :REACTION"

            elif ("nmr for" in emailsubject0.lower()):
               ttmp2 = ireplace("FOR","for",emailsubject0)
               esmiles0 = ttmp2.split('for')[1]
               reactions = "NMR: "
               reactions += esmiles0
               reactions += " :NMR"

            elif ("output deck for" in emailsubject0.lower()) or ("outputdeck for" in emailsubject0.lower()) or ("nwoutput for" in emailsubject0.lower()):
               ttmp2 = ireplace("FOR","for",emailsubject0)
               esmiles0 = ttmp2.split('for')[1]
               reactions = "NWOUTPUT: "
               reactions += esmiles0
               reactions += " :NWOUTPUT"

            elif "submitesmiles for" in emailsubject0.lower():
               ttmp2 = ireplace("FOR","for",emailsubject0)
               esmiles0 = ttmp2.split('for')[1]
               reactions = "SUBMITESMILES: "
               reactions += esmiles0
               reactions += " :SUBMITESMILES"

            elif "xyz for" in emailsubject0.lower():
               ttmp2 = ireplace("FOR","for",emailsubject0)
               esmiles0 = ttmp2.split('for')[1]
               reactions = "XYZFILE: "
               reactions += esmiles0
               reactions += " :XYZFILE"

            elif ("list all esmiles"  in emailsubject0.lower()) or ("listallesmiles"  in emailsubject0.lower()):
               reactions = "listallesmiles\n"

            elif ("list all reactions"  in emailsubject0.lower()) or ("listallreactions"  in emailsubject0.lower()):
               reactions = "listallreactions\n"

            elif "smarts" in emailsubject0.lower():
               ttmp2 = ireplace("SMARTS","smarts",emailsubject0)
               esmiles0 = ttmp2.split('smarts')[1]
               reactions = "smarts: "
               reactions += esmiles0
               reactions += " :smarts"

            else:
               reactions = "MOLECULE: "
               reactions += emailsubject0
               reactions += " :MOLECULE"
         else:
            msg = ireplace("molecule", "MOLECULE", msg)
            if ((("MOLECULE:" in msg) and (":MOLECULE" in msg)) or (("REACTION:" in msg) and (":REACTION" in msg))):
               reactions = msg
            else:
               if ("-->" in msg):
                  reactions = "REACTION: "
                  reactions += msg
                  reactions += " :REACTION"


      entry_added = False
      if (reactions!=''):
         entry_added = True
         reactions += "\n"

        # #### loadmyoptions to the start of reactions string ###
        # if (loadmyoptions!=''): 
        #    reactions = loadmyoptions + "\n" + reactions
         

         ofile = open(wrkdir + "/" + aname1,'w')
         ofile.write(reactions)
         ofile.write("\nemailfrom: " + emailfrom + " :emailfrom\n")
         ofile.write("\nemailcc: " + emailcc + " :emailcc\n")
         ofile.close()
         cmd = chemdb_fetch_reactions + " -e " + wrkdir + '/' + aname1 + ' ' + wrkdir + '/' + aname3 + ' ' +  wrkdir + '/' + aname2

         #### save arrows.txt.debug debug file ####
         dfile = open(wrkdir + "/arrows.txt.debug",'w')
         dfile.write(reactions)
         dfile.write("\nemailfrom: " + emailfrom + " :emailfrom\n")
         dfile.write("\nemailcc: " + emailcc + " :emailcc\n")
         dfile.close()
         #### save arrows.txt.debug debug file ####

         try:
            print "running cmd:",cmd
            tsg += "running cmd:" + cmd + "\n"
            result = subprocess.check_output(cmd,shell=True)
            print
            print result
            print
            imagelist = result.split("imagelist:")[1].split(":imagelist")[0]
            tsg += "\n" + result + "\n"
            success = "All requests to Arrows were successful." in result
         except:
            success = False

         ### add arrows entry to arrows_collection  ###
         arrow_entry = {}
         tt = time.localtime()
         gt = time.gmtime()
         arrow_entry['submit_time']    = pickle.dumps(tt)
         arrow_entry['submit_gm_time'] = pickle.dumps(gt)
         arrow_entry['date_time']      = time.strftime('%Y-%m-%d %H:%M:%S')
         arrow_entry['count'] = 1
         arrow_entry['reactions']    = reactions
         arrow_entry['emailsubject'] = emailsubject
         arrow_entry['emailfrom']    = emailfrom
         arrow_entry['emailcc']      = emailcc
         arrow_entry['queue_number']  = qnumber_collection.find_one({'queue':'arrows'})['count']
         qq  = qnumber_collection.update({'queue':'arrows'},{'$inc':{'count':1}},upsert=False,multi=False)


         if (success):
            qqq = dqueue_collection.insert(arrow_entry)
            print "dqueue_collection.insert = ",qqq
         else:
            qqq = arrows_collection.insert(arrow_entry)
            print "arrows_collection.insert = ",qqq


         ### email results ###
         if headermyoptions!='':
            with open(wrkdir + '/' + aname2,'r') as ff1: aatmp = ff1.read()
            aatmp = headermyoptions + "\n" + aatmp
            with open(wrkdir + '/' + aname2,'w') as ff2: ff2.write(aatmp)

         subjct = "Arrows Re: " + emailsubject
         cmd2 = send_smtp_image + " -m " +'\"' + emailfrom + emailcc + '\"' + ' -j \"' + subjct + '\"  -i \"' + imagelist  +'\" ' + wrkdir + '/' + aname3 + ' '+ wrkdir + '/' + aname2
         print "cmd2= " + cmd2
         tsg += "running cmd2:" + cmd2 + "\n"
         try:
            result2 = subprocess.check_output(cmd2,shell=True)
         except:
            result2 = "arrows.x: failed to send email"
         print
         print result2
         tsg += "\n" + result2 + "\n"

         ### remove png files in imagelist ###
         for img in imagelist.split()[0::2]:
            try:
               os.unlink(img)
            except:
               print "failed to remove " + img

      #### ARROWS parsing ####


   #### remove arrows2 files ####
   if (entry_added):
      try:
         os.unlink(wrkdir + "/" + aname1)
      except:
         print "failed to remove " + wrkdir + "/" + aname1

      try:
         os.unlink(wrkdir + "/" + aname2)
      except:
         print "failed to remove " + wrkdir + "/" +  aname2

      try:
         os.unlink(wrkdir + "/" + aname3)
      except:
         print "failed to remove " + wrkdir + "/" +  aname3


   #### remove nwjobfiles files ####
   if (nwentry_added):
      try:
         os.unlink(wrkdir + "/" + bname1)
      except:
         print "failed to remove " + wrkdir + "/" +  bname1

      try:
         os.unlink(wrkdir + "/" + bname2)
      except:
         print "failed to remove " + wrkdir + "/" +  bname2



   return tsg







############################### Main Program  ####################################

### lockfile ###
if os.path.isfile(lockfilename): exit()
with open(lockfilename,'w') as lfile: lfile.write("iamlocked\n")

try:
   tsg = parse_email()
except:
   tsg = "arrows: Failed reading and parsing email.\n"


#### read arrows email ###



### write output ###
oofile = open(wrkdir + "/arrows.parse","w")
oofile.write(tsg)
oofile.close()

#### remove arrows2 files ####
#if (entry_added):
#   try:
#      os.unlink(wrkdir + "/" + aname1)
#   except:
#      print "failed to remove " + wrkdir + "/" + aname1
#
#   try:
#      os.unlink(wrkdir + "/" + aname2)
#   except:
#      print "failed to remove " + wrkdir + "/" +  aname2

### remove lockfilename ###
try:
   os.unlink(lockfilename)
except:
   print "failed to remove " + lockfilename
