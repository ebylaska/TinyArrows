#!/usr/bin/python
from flask import Flask, jsonify, render_template,request,redirect,url_for,send_from_directory,Response
from flask import abort
from werkzeug.utils import secure_filename
import os,subprocess,urllib,time,random,requests,zipfile,math,yaml

###################### ARROWS Locations #######################
#ARROWS_HOME     = '/Users/bylaska/Public/TinyArrows'
ARROWS_HOME     = __file__.split("TinyArrows")[0] + "TinyArrows"

ARROWS_API_HOME = 'http://localhost:5000/api/'
###################### ARROWS Locations #######################

#UPLOAD_FOLDER = '/tmp/'
UPLOAD_FOLDER = ARROWS_HOME + '/Public/uploads/'
ALLOWED_EXTENSIONS = set(['cube', 'out', 'nwout', 'nwo', 'nw', 'eap', 'xyz', 'emotion', 'ion_motion', 'fei','eigmotion','dipole_motion','POWER_SPECTRUM','dipole_powerspectrum','VELOCITY_SPECTRUM','yaml','note','txt', 'inp', 'dat', 'mol', 'psp', 'hist', 'gr', 'cif', 'meta_gaussians','neb_epath','neb_final_epath', 'json','csv','PAIR_DISTRIBUTION'])


tar                     = "/bin/tar -czf " 
chemdb_fetch_reactions  = ARROWS_HOME + "/bin/chemdb_fetch_reactions5 --arrows_api=" + ARROWS_API_HOME + " -e "
chemdb_fetch_reactions0 = ARROWS_HOME + "/bin/chemdb_fetch_reactions5 --arrows_api=" + ARROWS_API_HOME + " "
chemdb_queue            = ARROWS_HOME + "/bin/chemdb_queue --arrows_api=" + ARROWS_API_HOME + " "
chemdb_balance_reaction = ARROWS_HOME + "/bin/chemdb_balance_reaction9f --arrows_api=" + ARROWS_API_HOME + " "
tnt_submit              = ARROWS_HOME + "/bin/tnt_submit5 --arrows_api=" + ARROWS_API_HOME + " -f "

chemdb_queue_nwchem     = ARROWS_HOME + "/bin/chemdb_queue_nwchem "
chemdb_fetch_esmiles5   = ARROWS_HOME + "/bin/chemdb_fetch_esmiles5 "
chemdb_image0           = ARROWS_HOME + "/bin/chemdb_image0 -f "
chemdb_eric             = ARROWS_HOME + "/bin/chemdb_eric  "
chemdb_osra             = ARROWS_HOME + "/bin/chemdb_osra  "
chemdb_molcalc          = ARROWS_HOME + "/bin/chemdb_molcalc "
queue_nwchem3           = ARROWS_HOME + "/bin/queue_nwchem3 -s -a"
cifocd_gennw            = ARROWS_HOME + "/bin/cifocd_gennw "
esmiles2xyz             = ARROWS_HOME + "/bin/esmiles2xyz "
wrkdir                  = ARROWS_HOME + "/Work"
templatedir             = "templates"
templatedir2            = "templates2"
staticdir               = "static"
staticdir2              = "static2"
reactiondir             = "reaction"
chemdbdir               = "chemdb_hold"
counterdir              = "counters"
namecount = 0
esmiles2xyzblocked = 0



#headerfigure = ['<a href="https://dl.dropboxusercontent.com/s/1fdkluujb97tr0b/banner2.gif"><img src="https://dl.dropboxusercontent.com/s/1fdkluujb97tr0b/banner2.gif" alt="Arrows Banner Movie"> </a>', '<a href="https://dl.dropboxusercontent.com/s/en5l9l7l31ggz6e/EMSL_banner.jpg"><img src="https://dl.dropboxusercontent.com/s/en5l9l7l31ggz6e/EMSL_banner.jpg" alt="EMSL Computing Banner" height="162" width="450" border=0 /></a>', '<a href="https://dl.dropboxusercontent.com/s/rcoee0m9urc4e3o/Surface-uprot.gif"><img src="https://dl.dropboxusercontent.com/s/rcoee0m9urc4e3o/Surface-uprot.gif" alt="Arrows Movie" width="200" height="200"> </a>', '<a href="https://dl.dropboxusercontent.com/s/chxhlvamd8ro356/ArrowsBeaker2.gif"><img src="https://dl.dropboxusercontent.com/s/chxhlvamd8ro356/ArrowsBeaker2.gif" alt="Arrows Movie"> </a>']

headerfigure = ['<a href="https://dl.dropboxusercontent.com/s/1fdkluujb97tr0b/banner2.gif"><img src="https://dl.dropboxusercontent.com/s/1fdkluujb97tr0b/banner2.gif" alt="Arrows Banner Movie"> </a>', '<a href="https://dl.dropboxusercontent.com/s/en5l9l7l31ggz6e/EMSL_banner.jpg"><img src="https://dl.dropboxusercontent.com/s/en5l9l7l31ggz6e/EMSL_banner.jpg" alt="EMSL Computing Banner" height="162" width="450" border=0 /></a>', '<a href="https://dl.dropboxusercontent.com/s/rcoee0m9urc4e3o/Surface-uprot.gif"><img src="https://dl.dropboxusercontent.com/s/rcoee0m9urc4e3o/Surface-uprot.gif" alt="Arrows Movie" width="200" height="200"> </a>', '<a href="{{url_for(\'static\', filename=\'arrows-static/ArrowsBeaker2.gif\')}}"><img src="{{url_for(\'static\', filename=\'arrows-static/ArrowsBeaker2.gif\')}}" alt="Arrows Movie"> </a>']

##### define the arrows logos #####
ArrowsHeader = '''
   <head> <meta http-equiv="content-type" content="text/html; charset=UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, target-densitydpi=device-dpi"> <meta charset="utf-8"><link rel="icon" type="image/png" sizes="32x32" href="https://dl.dropboxusercontent.com/s/r0gjpgxp8byjbzr/favicon-32x32.png"><link rel="icon" type="image/png" sizes="96x96" href="https://dl.dropboxusercontent.com/s/k0kyp30ale2pkod/favicon-96x96.png"><link rel="icon" type="image/png" sizes="16x16" href="https://dl.dropboxusercontent.com/s/0l0w2wk9wfxt4el/favicon-16x16.png"><style type="text/css"> </style> </head>

   <center> <font color="74A52B" size="+2"><p><b>Results from an EMSL Arrows Request</b></p></font></center>
   <center> <p>Making molecular modeling accessible by combining NWChem, databases, web APIs (<a href="%s">%s</a>), and email (arrows@emsl.pnnl.gov)</p> </center>
   <center> %s </center>
''' % (ARROWS_API_HOME,ARROWS_API_HOME,headerfigure[3])

ArrowsHeader2 = '''
   <center> <font color="darkgreen" size="+2"><p><b> EMSL Arrows Microsoft Quantum Development Kit Queue</b></p></font></center>
   <center> <p>Making molecular modeling accessible by combining NWChem, databases, web APIs (<a href="https://arrows.emsl.pnnl.gov/api/">https://arrows.emsl.pnnl.gov/api</a>), and email (arrows@emsl.pnnl.gov)</p> </center>
   <center><a href="https://arrows.emsl.pnnl.gov/api/qsharp_chem">Link back to Microsoft Quantum Editor</a></p></center>
   <center> %s </center>
''' % (headerfigure[1]+headerfigure[0])





def evalnum(s):
   try:
      return int(s)
   except ValueError:
      return float(s)




#### geturlresult function ####
def geturlresult(url):
    try:
        connection = urllib.urlopen(url)
    except urllib.HTTPError:
        return ""
    else:
        return connection.read().rstrip()


def ireplace(old, new, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(old)
    return text


def parse_output(datatype,parsing1,data):
   try:
      if ((parsing1.lower().strip()=="e(gas)")    or (parsing1.lower().strip()=="erxn(gas)")) and (datatype=="molecule"):
         data = data.split("energy           =")[1].split("Hartrees")[0].strip()
      elif ((parsing1.strip()=="zpe(gas)")) and (datatype=="molecule"):
         hh = evalnum(data.split("zero-point correction to energy                 =")[1].split("(")[1].split(")")[0].strip())
         data = "%.6f" % (hh)
      elif ((parsing1.strip()=="e_zpe(gas)")    or (parsing1.strip()=="erxn_zpe(gas)")) and (datatype=="molecule"):
         ee = evalnum(data.split("energy           =")[1].split("Hartrees")[0].strip())
         hh = evalnum(data.split("zero-point correction to energy                 =")[1].split("(")[1].split(")")[0].strip())
         data = "%.6f" % (ee+hh)
      elif ((parsing1.strip()=="h(gas)")    or (parsing1.strip()=="hrxn(gas)")) and (datatype=="molecule"):
         ee = evalnum(data.split("energy           =")[1].split("Hartrees")[0].strip())
         hh = evalnum(data.split("enthalpy correct.=")[1].split("Hartrees")[0].strip())
         data = "%.6f" % (ee+hh)
      elif ((parsing1.lower().strip()=="g(gas)")    or (parsing1.lower().strip()=="grxn(gas)")) and (datatype=="molecule"):
         ee = evalnum(data.split("energy           =")[1].split("Hartrees")[0].strip())
         hh = evalnum(data.split("enthalpy correct.=")[1].split("Hartrees")[0].strip())
         ss = evalnum(data.split("entropy          =")[1].split("cal/mol-K")[0].strip())/(23.06*27.2116*1000.0)
         data = "%.6f" % (ee+hh-298.0*ss)
      elif ((parsing1.lower().strip()=="solvation") or (parsing1.lower().strip()=="delta_solvation")) and (datatype=="molecule"):
         cc = evalnum(data.split("solvation energy =")[1].split("kcal/mol")[0].strip())/(23.06*27.2116)
         data = "%.6f" % (cc)
      elif ((parsing1.lower().strip()=="g(aq)")    or (parsing1.lower().strip()=="grxn(aq)")) and (datatype=="molecule"):
         ee = evalnum(data.split("energy           =")[1].split("Hartrees")[0].strip())
         hh = evalnum(data.split("enthalpy correct.=")[1].split("Hartrees")[0].strip())
         ss = evalnum(data.split("entropy          =")[1].split("cal/mol-K")[0].strip())/(23.06*27.2116*1000.0)
         cc = evalnum(data.split("solvation energy =")[1].split("kcal/mol")[0].strip())/(23.06*27.2116)
         data = "%.6f" % (ee+hh-298.0*ss+cc)
      elif ((parsing1.lower().strip()=="homo") or (parsing1.lower().strip()=="alpha_homo")) and (("restricted" in data) or ("alpha" in data)) and (datatype=="molecule"):
         eigs = data.split("spin            eig      occ")[1].split("+----------------------------------------+")[0].strip().split("\n")
         homo = -9.0e+9
         for ln in eigs[1:]:
            if ("restricted" in ln) or ("alpha" in ln):
               ss = ln.split()
               if ((ss[2]=="2.00") or (ss[2]=="1.00")) and (evalnum(ss[1])>homo):
                  homo = evalnum(ss[1])
                  data = ss[1]
      elif ((parsing1.lower().strip()=="lumo") or (parsing1.lower().strip()=="alpha_lumo")) and (("restricted" in data) or ("alpha" in data)) and (datatype=="molecule"):
         eigs = data.split("spin            eig      occ")[1].split("+----------------------------------------+")[0].strip().split("\n")
         lumo = 9.0e+9
         for ln in eigs[1:]:
            if ("restricted" in ln) or ("alpha" in ln):
               ss = ln.split()
               if (ss[2]=="0.00") and (evalnum(ss[1])<lumo):
                  lumo = evalnum(ss[1])
                  data = ss[1]
      elif (parsing1.lower().strip()=="beta_homo") and ("beta" in data) and (datatype=="molecule"):
         eigs = data.split("spin            eig      occ")[1].split("+----------------------------------------+")[0].strip().split("\n")
         homo = -9.0e+9
         for ln in eigs[1:]:
            if ("beta" in ln):
               ss = ln.split()
               if ((ss[2]=="2.00") or (ss[2]=="1.00")) and (evalnum(ss[1])>homo):
                  homo = evalnum(ss[1])
                  data = ss[1]
      elif (parsing1.lower().strip()=="beta_lumo") and ("beta" in data) and (datatype=="molecule"):
         eigs = data.split("spin            eig      occ")[1].split("+----------------------------------------+")[0].strip().split("\n")
         lumo = 9.0e+9
         for ln in eigs[1:]:
            if ("beta" in ln):
               ss = ln.split()
               if (ss[2]=="0.00") and (evalnum(ss[1])<lumo):
                  lumo = evalnum(ss[1])
                  data = ss[1]
      elif ((parsing1.lower().strip()=="e(gas)")    or (parsing1.lower().strip()=="erxn(gas)")) and (datatype=="reaction"):
         data = data.split("Grxn(aq)")[-1].split("-- in Hartrees")[0].split(":")[-1].split()[0]
      elif ((parsing1.lower().strip()=="h(gas)")    or (parsing1.lower().strip()=="hrxn(gas)")) and (datatype=="reaction"):
         data = data.split("Grxn(aq)")[-1].split("-- in Hartrees")[0].split(":")[-1].split()[1]
      elif ((parsing1.lower().strip()=="g(gas)")    or (parsing1.lower().strip()=="grxn(gas)")) and (datatype=="reaction"):
         data = data.split("Grxn(aq)")[-1].split("-- in Hartrees")[0].split(":")[-1].split()[2]
      elif ((parsing1.lower().strip()=="solvation") or (parsing1.lower().strip()=="delta_solvation")) and (datatype=="reaction"):
         data = data.split("Grxn(aq)")[-1].split("-- in Hartrees")[0].split(":")[-1].split()[3]
      elif ((parsing1.lower().strip()=="g(aq)")    or (parsing1.lower().strip()=="grxn(aq)")) and (datatype=="reaction"):
         data = data.split("Grxn(aq)")[-1].split("-- in Hartrees")[0].split(":")[-1].split()[4]
      else:
         while ("split:" in parsing1) and (":split" in parsing1):
            midstr   = parsing1.split("split:")[1].split(":split")[0]
            parsing1 = parsing1.replace("split:"+midstr+":split","")
            if ("|" in midstr):
               sstr = midstr.split("|")[0]
               ii = evalnum(midstr.split("|")[1])
               data = data.split(sstr)[ii]
            else:
               data = data.strip()

      if (data==''): data = "not available - submitted?"
   except:
      data = "not available - submitted?"

   return data


def parse_matrix_elements(outfile):
   mdict = {}
   mdict['format'] = {'version':"0.1"}
   mdict['generator'] = {'source': 'nwchem'}
   mdict['generator']['version'] = '0.1.2.3'
   mdict['integral_sets'] = [{'metadata': {'molecule_name':'unknown'}}]
   mdict['integral_sets'][0]['basis_set'] = {'name':'unknown', 'type':'gaussian'}
   mdict['integral_sets'][0]['geometry'] = {'units':'angstrom','coordinate_system':'cartesian','symmetry':'c1','atoms':[]}
   mdict['integral_sets'][0]['coulomb_repulsion'] = {'units':'hartree','value':0.0}
   mdict['integral_sets'][0]['scf_energy'] = {'units':'hartree','value':0.0}
   mdict['integral_sets'][0]['scf_energy_offset'] = {'units':'hartree','value':0.0}
   #mdict['integral_sets']['ccsd_energy'] = {'units':'hartree','value':0.0}
   mdict['integral_sets'][0]['energy_offset'] = {'units':'hartree','value':0.0}
   mdict['integral_sets'][0]['fci_energy'] = {'lower':0.0, 'units':'hartree','upper':0.0,'value':0.0}
   mdict['integral_sets'][0]['n_orbitals'] = 0
   mdict['integral_sets'][0]['n_electrons'] = 0
   mdict['integral_sets'][0]['hamiltonian'] = {'one_electron_integrals':{'units':'hartree','format':'sparse','values':[]}, 'two_electron_integrals':{'units':'hartree','format':'sparse','index_convention':'mulliken','values':[]}}

   if (os.path.exists(outfile)):
      try:
         h1set = False
         b1set = False
         b2set = False
         e1set = False
         e1count = 0
         gsenergy = 0.0
         g1set = False
         s0set = False
         s1set = False
         s2set = False
         v2set = False
         virton = False
         ofile = open(outfile,'r')
         for line in ofile:
            if (line.find("Number of active orbitals") != -1):
               mdict['integral_sets'][0]['n_orbitals'] = eval(line.split()[4])
            if (line.find("Number of active alpha electrons") != -1):
               mdict['integral_sets'][0]['n_electrons'] += eval(line.split()[5])
            if (line.find("Number of active beta electrons") != -1):
               mdict['integral_sets'][0]['n_electrons'] += eval(line.split()[5])
            if (line.find("number of electrons: spin up=") != -1):
               if ((line.split()[5].isdigit()) and (line.split()[11].isdigit())):
                  mdict['integral_sets'][0]['n_electrons'] = eval(line.split()[5]) + eval(line.split()[11])
            if (line.find("number of orbitals : spin up=") != -1):
               if (line.split()[6].isdigit()):
                  mdict['integral_sets'][0]['n_orbitals'] = eval(line.split()[6])

            if (virton):
               if (len(line.split()) > 1):
                  mdict['integral_sets'][0]['n_orbitals'] += 1
               else:
                  virton = False
            if (line.find("virtual orbital energies:") != -1): 
               virton = True
            


            #if (line.find("CCSD total energy / hartree       =") != -1):
            #    gsenergy = eval(line.split()[6])
            #    state = {'state':{'label':'|G>','superposition':[], 'energy':{'units':'hartree','value': gsenergy}}}
            #   mdict['integral_sets']['ccsd_energy']['value'] = eval(line.split()[6])
            if (line.find("ion-ion   energy    :") != -1):
               mdict['integral_sets'][0]['coulomb_repulsion']['value'] = eval(line.split()[3])
            if (line.find("total     energy    :") != -1):
               mdict['integral_sets'][0]['scf_energy']['value'] = eval(line.split()[3])
            if (line.find("EHF(total)         =") != -1):
               mdict['integral_sets'][0]['scf_energy']['value'] = eval(line.split()[2])
            if (line.find("Shift (HFtot-HFA)  =") != -1):
               mdict['integral_sets'][0]['scf_energy_offset']['value'] = eval(line.split()[3])
            if (line.find("Northwest Computational Chemistry Package (NWChem)") != -1):
               mdict['generator']['version'] = line.split()[5]
            if (line.find("enrep_tce =") != -1):
               mdict['integral_sets'][0]['coulomb_repulsion']['value'] = eval(line.split()[2])

            if (line.find("end_two_electron_integrals") != -1):
               v2set = False

            if (v2set):
               ss = line.strip().split()
               mdict['integral_sets'][0]['hamiltonian']['two_electron_integrals']['values'].append([eval(ss[0]),eval(ss[1]),eval(ss[2]),eval(ss[3]),eval(ss[4])])

            if (line.find("end_one_electron_integrals") != -1):   h1set = False;
            if (line.find("begin_two_electron_integrals") != -1): h1set = False; v2set = True

            if (h1set):
               ss = line.split()
               mdict['integral_sets'][0]['hamiltonian']['one_electron_integrals']['values'].append([eval(ss[0]),eval(ss[1]),eval(ss[2])])

            if (line.find("begin_one_electron_integrals") != -1): h1set = True
            if (g1set):
               ss = line.split()
               if (len(ss)<1): 
                  g1set = False
               else:
                  tt = {'name':ss[1], 'coords':[eval(ss[3]),eval(ss[4]),eval(ss[5])]}
                  mdict['integral_sets'][0]['geometry']['atoms'].append(tt)
            if ('#' not in line) and (line.find(" ---- ---------------- ---------- -------------- -------------- --------------") != -1): g1set = True

            if (b1set):
               ss = line.split()
               if (len(ss)<1): 
                  b1set = False
                  b2set = True
               else:
                  tt = {'name':ss[1], 'type': 'gaussian'}
                  mdict['integral_sets'][0]['basis_set'] = tt
                  #mdict['integral_sets']['basis_set'].append(tt)
            if ('#' not in line) and (not b2set) and (line.find(" ---------------- ------------------------------  ------  ---------------------") != -1): b1set = True

            if (('#' not in line) and ('wavefnc cutoff=' in line)):
               ss = line.split()
               tt = {'name': '%.0fRy' % (2*eval(ss[2])), 'type': 'planewave'}
               mdict['integral_sets'][0]['basis_set'] = tt

            if (e1set):
               ss = line.split()
               if (line.find("Summary of allocated global arrays") != -1): 
                  e1set = False
                  mdict['integral_sets'][0]['initial_state_suggestions'].append(state)
               elif (line.find("Excitation energy / hartree =") != -1): 
                  if (e1count>0):
                     mdict['integral_sets'][0]['initial_state_suggestions'].append(state)
                  e1count += 1
                  chi = "|E%d>" % (e1count-1)
                  state = {'state':{'label':chi,'superposition':[], 'energy':{'units':'hartree','value': gsenergy+eval(ss[5])}}}
               elif (line.find("CCSD total energy / hartree       =") != -1):
                  gsenergy = eval(line.split()[6])
                  state = {'state':{'label':'|G>','superposition':[], 'energy':{'units':'hartree','value': gsenergy}}}
                  e1count += 1
               elif (s0set):
                  if (len(ss)<3):
                     s0set = False
                  else:
                     sss = [eval(ss[0])] + line.replace(":","").split()[1:]
                     state['state']['superposition'].append(sss)
               elif (line.find("Reference string") != -1): 
                  s0set = True
               elif (s1set):
                  if (len(ss)<3):
                     s1set = False
                  else:
                     sss = [eval(ss[0])] + line.replace(":","").split()[1:]
                     state['state']['superposition'].append(sss)
               elif (line.find("Singles strings") != -1): 
                  s1set = True
           
               elif (s2set):
                  if (len(ss)<3):
                     s2set = False
                  else:
                     sss = [eval(ss[0])] + line.replace(":","").split()[1:]
                     state['state']['superposition'].append(sss)
               elif (line.find("Doubles strings") != -1): 
                  s2set = True

            #if (line.find("No. of excited states :") != -1):
            if (line.find("CCSD iterations") != -1):
                  e1set = True
                  mdict['integral_sets'][0]['initial_state_suggestions'] = []

         ofile.close()
         #mblob = yaml.dump(mdict, default_flow_style=False)
         #mblob = yaml.dump(mdict)
      except:
         mdict = {}
   return mdict








###########################################
#                                         #
#             xyz2cif                     #
#                                         #
###########################################
def xyz2cif(xyzdat,cell):
   try:
      a1 = cell.split("a1=<")[1].split(">")[0].strip().split()
      a2 = cell.split("a2=<")[1].split(">")[0].strip().split()
      a3 = cell.split("a3=<")[1].split(">")[0].strip().split()
      for i in range(3):
         a1[i] = eval(a1[i])
         a2[i] = eval(a2[i])
         a3[i] = eval(a3[i])
      aa = math.sqrt(a1[0]**2 + a1[1]**2 +a1[2]**2)
      bb = math.sqrt(a2[0]**2 + a2[1]**2 +a2[2]**2)
      cc = math.sqrt(a3[0]**2 + a3[1]**2 +a3[2]**2)

      d2 = (a2[0]-a3[0])**2 + (a2[1]-a3[1])**2 + (a2[2]-a3[2])**2
      alpha = (bb*bb + cc*cc - d2)/(2.00*bb*cc)
      alpha = math.acos(alpha)*180.00/math.pi

      d2 = (a3[0]-a1[0])**2 + (a3[1]-a1[1])**2 + (a3[2]-a1[2])**2
      beta = (cc*cc + aa*aa - d2)/(2.00*cc*aa)
      beta = math.acos(beta)*180.00/math.pi

      d2 = (a1[0]-a2[0])**2 + (a1[1]-a2[1])**2 + (a1[2]-a2[2])**2
      gamma = (aa*aa + bb*bb - d2)/(2.00*aa*bb)
      gamma = math.acos(gamma)*180.00/math.pi

      a = aa*0.529177
      b = bb*0.529177
      c = cc*0.529177
      for i in range(3):
         a1[i] *= 0.529177
         a2[i] *= 0.529177
         a3[i] *= 0.529177

   except:
      a1 = [50.0,  0.0,  0.0]
      a2 = [ 0.0, 50.0,  0.0]
      a3 = [ 0.0,  0.0, 50.0]
      a = b = c = 50.0
      alpha = beta = gamma = 90.0

   b1 = [0]*3
   b1[0] = a2[1]*a3[2] - a2[2]*a3[1]
   b1[1] = a2[2]*a3[0] - a2[0]*a3[2]
   b1[2] = a2[0]*a3[1] - a2[1]*a3[0]

   b2 = [0]*3
   b2[0] = a3[1]*a1[2] - a3[2]*a1[1]
   b2[1] = a3[2]*a1[0] - a3[0]*a1[2]
   b2[2] = a3[0]*a1[1] - a3[1]*a1[0]

   b3 = [0]*3
   b3[0] = a1[1]*a2[2] - a1[2]*a2[1]
   b3[1] = a1[2]*a2[0] - a1[0]*a2[2]
   b3[2] = a1[0]*a2[1] - a1[1]*a2[0]


   volume = a1[0]*b1[0] + a1[1]*b1[1] + a1[2]*b1[2]
   for i in range(3):
      b1[i] = b1[i]/volume
      b2[i] = b2[i]/volume
      b3[i] = b3[i]/volume

   msg = '''data_arrows_pspw 

_audit_creation_date   Wed Apr 19 18:30:16 2017
_audit_creation_method    generated by EMSL Arrows


_cell_length_a      %12.4f
_cell_length_b      %12.4f
_cell_length_c      %12.4f
_cell_angle_alpha   %12.4f
_cell_angle_beta    %12.4f
_cell_angle_gamma   %12.4f

_symmetry_space_group_name_H-M     P1  

loop_
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z''' % (a,b,c,alpha,beta,gamma)

   msg += "\n"
   for ll in xyzdat.strip().split("\n")[2:]:
      ss = ll.split()
      symb = ss[0]
      x = eval(ss[1])
      y = eval(ss[2])
      z = eval(ss[3])
      f1 = x*b1[0] + y*b1[1] + z*b1[2]
      f2 = x*b2[0] + y*b2[1] + z*b2[2]
      f3 = x*b3[0] + y*b3[1] + z*b3[2]
      msg += "%s %12.6f %12.6f %12.6f\n" % (symb,f1+0.5,f2+0.5,f3+0.5)

   return msg






###########################################
#                                         #
#             nwinput2jsmol               #
#                                         #
###########################################

def nwinput2jsmol(backgroundcolor,nwinput):
   staticdir = ARROWS_HOME + "/Public/static/"
   msg4 = ''
   if "geometry" not in nwinput:
      return msg4

   ### fetch xyzdat ###
   xxx = nwinput.split("geometry")[-1].split("end")[0].strip()
   yyy = xxx.split("\n")
   zzz = '\n'.join(yyy[1:])
   nion   = len(zzz.split("\n"))
   xyzdat = "%d\n\n" % nion
   xyzdat += zzz + "\n"
   xx = random.randint(0,999999)

   cell = ''
   if "fcc 38.0" in nwinput:
      cell = ''' supercell:
      cell_name:  cell_default                                      
      lattice:    a1=<  19.000  19.000   0.000 >
                  a2=<  19.000   0.000  19.000 >
                  a3=<   0.000  19.000  19.000 >
      reciprocal: b1=<   0.165   0.165  -0.165 >
                  b2=<   0.165  -0.165   0.165 >
                  b3=<  -0.165   0.165   0.165 >
      lattice:    a=      26.870 b=     26.870 c=      26.870
                  alpha=  60.000 beta=  60.000 gamma=  60.000
                  omega=     13718.0 '''
   elif "lattice_vectors" in nwinput:
      a1 = nwinput.split("lattice_vectors")[1].strip().split('\n')[0]
      a2 = nwinput.split("lattice_vectors")[1].strip().split('\n')[1]
      a3 = nwinput.split("lattice_vectors")[1].strip().split('\n')[2]
      cell = ''' supercell:
      cell_name:  cell_default                                      
      lattice:    a1=< %s >
                  a2=< %s >
                  a3=< %s > ''' % (a1,a2,a3)


   if cell!='':
      xyzfilename = "tmp/molecule-jsmol-%d.cif" % xx
      xyzlist = xyzdat.strip().split("\n")
      nion = eval(xyzlist[0].strip())
      cifdat = ''
      while (len(xyzlist)>=(nion+2)):
         xyzdat0 = "\n".join(xyzlist[:nion+2])
         xyzlist = xyzlist[nion+2:]
         cifdat += xyz2cif(xyzdat0,cell)
      #cifdat = xyz2cif(xyzdat,cell)
      with open(staticdir + xyzfilename,'w') as ff:
         ff.write(cifdat)
   else:
      xyzfilename = "tmp/molecule-jsmol-%d.xyz" % xx
      with open(staticdir + xyzfilename,'w') as ff:
         ff.write(xyzdat)


   nion = eval(xyzdat.split("\n")[0].strip())
   nframes = (len(xyzdat.split("\n")))/(nion+2)
   alabel = ""
   count = 0
   for ll in xyzdat.strip().split("\n")[2:nion+2]:
      count += 1
      ss = ll.split()
      alabel += "select atomno=%d; label %s%d;" % (count,ss[0],count)

   #queuenumber = nwinput.split("START NWCHEM INPUT DECK -")[1].split("#")[0].strip()
   #msg4 += "Geometry for " + queuenumber + "\n"
   msg4 += "</pre>\n"
   msg4 += '<script type=\"text/javascript\" src=\"{{url_for(\'static\', filename=\'jsmol/JSmol.min.js\')}}\"></script>\n'
   msg4 += '''
   <script type="text/javascript"> 
      $(document).ready(
      function() {
            Info = {
            width: 500,
            height: 500,
            debug: false,
            j2sPath: "{{url_for('static', filename='jsmol/j2s')}}",
            //j2sPath: "jsmol/j2s",
            //color: "0x3BBC52",
            color: "%s",
            disableJ2SLoadMonitor: true,
            disableInitialConsole: true,
            addSelectionOptions: false,
            //serverURL: "http://10.0.1.99/jsmol.php",
            serverURL: "http://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
            use: "HTML5",
            readyFunction: null,
            script: "load  {{url_for('static', filename='%s')}} "
         }
         $("#jsmolmydiv").html(Jmol.getAppletHtml("jmolApplet0",Info))
   ''' % (backgroundcolor,xyzfilename)
   msg4 += '''
         $("#jsmolbtns").html(Jmol.jmolButton(jmolApplet0, "spin on","spin ON")+Jmol.jmolButton(jmolApplet0, "spin off","spin OFF")+Jmol.jmolButton(jmolApplet0, "%s","labels On")+Jmol.jmolButton(jmolApplet0, "select all;label off","labels Off") + Jmol.jmolButton(jmolApplet0, "unitcell 1; axes 1","unitcell/axes On") + Jmol.jmolButton(jmolApplet0, "unitcell 0; axes 0","unitcell/axes Off")) 
      }
      );
   </script>
   ''' % (alabel)

   msg4 += '<span id=jsmolmydiv></span>\n'
   msg4 += '<span id=jsmolbtns></span>\n'
   msg4 += '<br><font color="443322" size="2"><p><a href="http://wiki.jmol.org/index.php/JSmol">JSmol: an open-source HTML5 viewer for chemical structures in 3D</a></p></font><br>'
   msg4 += "<pre style=\"font-size:1.0em;color:black\">\n"

   return msg4



#############################################
#                                           #
#             addspaces_reaction            #
#                                           #
#############################################
def addspaces_reaction(reaction):
   tags = ['^','mult','theory','xc','solvation_type','basis','calculation_type','property','priority','geometry_generation']
   reaction2 = reaction[:]
   if (reaction2.find(">")!=-1):
      reaction2 = reaction2.replace(">","")
   if (reaction2.find("-->")==-1):
      reaction2 = reaction2.replace("--","-->")
   for tag1 in tags: reaction2 = reaction2.replace(tag1," " + tag1)
   return reaction2

#### parsetosmiles function ####
def parsetosmiles(str):
   global xyzdata
   ss = str.split()
   str2 = ''
   for s in ss:
      if 'kegg=' in s.lower():
         kegg = s.split('=')[1]
         mol = geturlresult("http://rest.kegg.jp/get/%s/mol" % kegg)
         smiles = mol2smiles(mol)
         if smiles=='': smiles='C'
         str2 += ' '
         str2 += smiles
      elif ('cid=' in s.lower()) or ('pubchem=' in s.lower()) :
         cid = s.split('=')[1]
         smiles = geturlresult("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/%s/property/CanonicalSMILES/TXT" % cid)
         if smiles=='': smiles='C'
         str2 += ' '
         str2 += smiles
      elif ('csid=' in s.lower()) or ('chemspider=' in s.lower()):
         csid = s.split('=')[1]
         rdfdata = geturlresult("http://rdf.chemspider.com/%s" % csid)
         if rdfdata=='':
            smiles='C'
         else:
            rdfdata2 = rdfdata.split('<chemdomain:SMILES')[1].split('</chemdomain:SMILES>')[0]
            smiles   = rdfdata2.split('<chemdomain:hasValue>')[1].split('</chemdomain:hasValue>')[0].strip()
         str2 += ' '
         str2 += smiles
      elif 'cas=' in s.lower():
         cas = s.split('=')[1]
         smiles = geturlresult("http://cactus.nci.nih.gov/chemical/structure/%s/smiles" % cas)
         if smiles=='': smiles='C'
         str2 += ' '
         str2 += smiles
      elif 'inchi=' in s.lower():
         smiles = InChI2smiles("InChI=" + s.split('=')[1])
         if smiles=='': smiles='C'
         str2 += ' '
         str2 += smiles
      else:
         str2 += ' '
         str2 += s
   str2 = str2.strip()

   return str2

def clean_upload_directory():
   ### remove files from uploaddir ###
   for the_file in os.listdir(UPLOAD_FOLDER):
      file_path = os.path.join(UPLOAD_FOLDER, the_file)
      try:
         if os.path.isfile(file_path):
            dt = time.time() - os.path.getmtime(file_path)
            if (dt>1800.0): os.unlink(file_path)
      except Exception as e:
         print(e)



def clean_directories():
   ### remove files from templatedir ###
   for the_file in os.listdir(templatedir+"/tmp"):
      file_path = os.path.join(templatedir+"/tmp", the_file)
      try:
         if os.path.isfile(file_path):
            if ('reaction' in file_path) or ('molecule' in file_path):
               dt = time.time() - os.path.getmtime(file_path)
               if (dt>1800.0): os.unlink(file_path)
      except Exception as e:
         print(e)

   ### remove files from staticdir ###
   for the_file in os.listdir(staticdir+"/tmp"):
      file_path = os.path.join(staticdir+"/tmp", the_file)
      try:
         if os.path.isfile(file_path):
            dt = time.time() - os.path.getmtime(file_path)
            #if (dt>1800.0): os.unlink(file_path)
            if (dt>864000.0): os.unlink(file_path)  #10days
      except Exception as e:
         print(e)


def resolve_images(result,html):
   imagelist = result.split("imagelist:")[1].split(":imagelist")[0]
   images = [(imagelist.split()[i],imagelist.split()[i+1]) for i in range(0,len(imagelist.split()),2)]
   for a in images:
      if os.path.isfile(a[0]):
         a1 = "cid:"+a[1]
         a2 = " {{url_for('static',filename='tmp/img-%s')}}" % (a[0].split("/")[-1])
         cmd8    = "cp " + a[0] + " " + staticdir + "/tmp/img-%s" %  (a[0].split("/")[-1])
         #result2 = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
         print("cmd8=",cmd8)
         result2 = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
         os.unlink(a[0])
         html    = html.replace(a1,a2)

   return html


def allowed_file(filename):
    allowed = False
    if '.' in filename:
       suffix = filename.rsplit('.', 1)[1]
    else:
       suffix = filename
    for a in ALLOWED_EXTENSIONS:
       if a in suffix: allowed = True
    return allowed
    #return '.' in filename and allowed
    #return '.' in filename and \
    #       filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def arrowsjobsrun():
   try:
      with open(counterdir+"/arrowsjobsrun",'r') as ff:
         aa = ff.read()
   except:
      aa = "?????"
   return (aa.strip())

def calculationscount():
   try:
      with open(counterdir+"/calculationscount",'r') as ff:
         aa = ff.read()
   except:
      aa = "?????"
   return (aa.strip())

def apivisited():
   try:
      with open(counterdir+"/apivisited",'r') as ff:
         aa = ff.read()
   except:
      aa = "?????"
   return (aa.strip())

def increment_apivisited():
   try:
      with open(counterdir+"/apivisited",'r') as ff:
         aa = ff.read()
      count = int(aa.strip()) + 1
      with open(counterdir+"/apivisited",'w') as ff:
         ff.write("%d" % count)
   except:
      print("increment_apivisited failed")


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]


@app.after_request
def after_request(response):
   response.headers.add('Access-Control-Allow-Origin', '*')
   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
   response.headers['Content-Security-Policy']=""
   response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
   return response



@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/api/esmiles2xyz/<esmiles0>', methods=['GET'])
def get_esmiles2xyz(esmiles0):
    global esmiles2xyzblocked

    if (esmiles2xyzblocked>=10): 
       return "system overloaded - please be kind"

    esmiles2xyzblocked += 1
    try:
       increment_apivisited()
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       esmiles0 = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       xyzfile   = wrkdir + "/jjarrows-%d.xyz" % ddrand
       cmd7 = esmiles2xyz + "-s " + '\"' + esmiles0 + '\" ' + xyzfile
       data = subprocess.check_output(cmd7,shell=True).decode("utf-8")
       os.unlink(xyzfile)
    except:
       data = '????'

    esmiles2xyzblocked -= 1

    return data


@app.route('/api/id/<int:task_id>', methods=['GET'])
def get_arrowid(task_id):
    try:
       increment_apivisited()
       #task = [task for task in tasks if task['id'] == task_id]
       esmiles = "id=%d" % task_id
       cmd7 = chemdb_fetch_esmiles5 + '\"' + esmiles + '\"'
       #data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       data = subprocess.check_output(cmd7,shell=True).decode("utf-8")
       if len(data) == 0: data=esmiles + " not found\n"
    except:
       data = '????'
    return data
    #return jsonify({'task': task[0]})


@app.route('/api/esmiles/<esmiles0>', methods=['GET'])
def get_esmiles(esmiles0):
    try:
       increment_apivisited()
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       esmiles0 = esmiles0.replace("%2F",'/')
       #print "esmiles=",esmiles0
       cmd7 = chemdb_fetch_esmiles5 + '\"' + esmiles0 + '\"'
       print("CMD7",cmd7)
       data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       if len(data) == 0: data=esmiles0 + " not found\n"
    except:
       data = '????'

    return data


@app.route('/api/osra/<path:esmiles0>', methods=['GET'])
def get_osra(esmiles0):
    try:
       increment_apivisited()
       #print "esmiles=",esmiles0
       cmd7 = chemdb_osra + '\"' + esmiles0 + '\"'
       #data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       data = subprocess.check_output(cmd7,shell=True).decode("utf-8")
       if len(data) == 0: data=esmiles0 + " not found\n"
    except:
       data = '????'

    html = "<html>\n"
    html += ArrowsHeader
    html += "<pre style=\"font-size:1.0em;color:black\">\n"
    html += data
    html += "</pre> </html>"

    return html



@app.route('/api/smarts/<smarts0>', methods=['GET'])
def get_smarts(smarts0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       smarts0  = smarts0.replace("\"",'')
       smarts0  = smarts0.replace("\'",'')
    
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("smarts: " + smarts0 + " :smarts usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> smarts failed </html>"

    return  data


@app.route('/api/frequency/<idfreq0>', methods=['GET'])
def get_frequency(idfreq0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       idfreq0  = idfreq0.replace("\"",'')
       idfreq0  = idfreq0.replace("\'",'')
       #ss = idfreq0.split()
       #tid = evalnum(ss[0])
       #tfnum = evalnum(ss[1])

       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("showfreq: " + idfreq0 + " :showfreq usehtml5\n")
          #ff.write("showfreq: %d %d  :showfreq usehtml5\n" % (tid,tfnum))
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> frequency failed </html>"

    return  data



@app.route('/api/listallesmiles/<nrows>', methods=['GET'])
def get_listallesmiles(nrows):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("listallesmiles\n usehtml5\n")
          if (nrows.isdigit()): ff.write(nrows +"\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> listallesmiles failed </html>"

    return  data


@app.route('/api/listallreactions/', methods=['GET'])
def get_listallreactions():
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("listallreactions\n usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> listallreactions failed </html>"

    return  data





@app.route('/api/submitesmiles/<esmiles0>', methods=['GET'])
def get_submitesmiles(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       machines0 = ''
       if "submitmachines{" in esmiles0:
          msg2 = esmiles0.split("submitmachines{")
          msg3 = msg2[1].split("}")[0]
          esmiles0 = esmiles0.replace("submitmachines{"+msg3+"}","")
          machines0 = msg3.strip()
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          if (machines0!=''): ff.write("submitmachines: " + machines0 + "  :submitmachines\n")
          ff.write("submitesmiles: " + esmiles0 + " :submitesmiles\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> submitesmiles failed </html>"

    return  data
                                             


@app.route('/api/molecule/<path:esmiles0>', methods=['GET'])
def get_molecule(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    has_parsing = False
    parsing1 = "" 
    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("!",'#')
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       print("molecule esmiles0=",esmiles0)
       if (("parse_output{" in esmiles0) and ("}" in esmiles0)):
          parsing1 = esmiles0.split("parse_output{")[1].split("}")[0]
          esmiles0 = esmiles0.replace("parse_output{"+parsing1+"}","")
          parsing1 = parsing1.strip()
          has_parsing = True

       machines0 = ''
       if "submitmachines{" in esmiles0:
          msg2 = esmiles0.split("submitmachines{")
          msg3 = msg2[1].split("}")[0]
          esmiles0 = esmiles0.replace("submitmachines{"+msg3+"}","")
          machines0 = msg3.strip()
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          if (machines0!=''): ff.write("submitmachines: " + machines0 + "  :submitmachines\n")
          if (has_parsing):
             ff.write("molecule: " + esmiles0 + " :molecule useascii\n")
          else:
             ff.write("molecule: " + esmiles0 + " :molecule usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       print("CMD7=",cmd7)
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       if (has_parsing) or ("useascii" in esmiles0):
          data = html
       else:
          html = resolve_images(result,html)
          with open(htmlfile1,'w') as ff: ff.write(html)
          data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> molecule failed </html>"

    if (parsing1!=''): data = parse_output("molecule",parsing1,data)

    return  data



@app.route('/api/nmr/<esmiles0>', methods=['GET'])
def get_nmr(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       machines0 = ''
       if "submitmachines{" in esmiles0:
          msg2 = esmiles0.split("submitmachines{")
          msg3 = msg2[1].split("}")[0]
          esmiles0 = esmiles0.replace("submitmachines{"+msg3+"}","")
          machines0 = msg3.strip()
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          if (machines0!=''): ff.write("submitmachines: " + machines0 + "  :submitmachines\n")
          ff.write("nmr: " + esmiles0 + " :nmr usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> nmr failed </html>"

    return  data


@app.route('/api/xyz/<esmiles0>', methods=['GET'])
def get_xyz(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("xyzfile: " + esmiles0 + " :xyzfile\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       #print("html=",html)
       data = html.split("====== start xyzfile ======")[1].split("====== end xyzfile ======")[0].strip() + "\n"
       html = "<html>\n"
       html += ArrowsHeader
       html += "<pre style=\"font-size:1.0em;color:black\">\n"
       html += data
       html += "</pre> </html>"
       with open(htmlfile1,'w') as ff: ff.write(html)

       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> xyz failed </html>"

    return  data


@app.route('/api/mol/<esmiles0>', methods=['GET'])
def get_mol(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("molfile: " + esmiles0 + " :molfile\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       #print("html=",html)
       data = html.split("====== start molfile ======")[1].split("====== end molfile ======")[0].strip() + "\n"
       html = "<html>\n"
       html += ArrowsHeader
       html += "<pre style=\"font-size:1.0em;color:black\">\n"
       html += data
       html += "</pre> </html>"
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)
       

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> mol failed </html>"

    return  data






@app.route('/api/nwoutput/<esmiles0>', methods=['GET'])
def get_nwoutput(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("nwoutput: " + esmiles0 + " :nwoutput\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> nwoutput failed </html>"

    return  data



@app.route('/api/nwoutput_download/<esmiles0>', methods=['GET'])
def get_nwoutput_download(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("nwoutput: " + esmiles0 + " :nwoutput\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### fetch the input deck from htmlfile ###
       with open(htmlfile,'r') as ff: data = ff.read()
       data = data.split("##################### start nwoutput #######################")[1]
       data = data.split("##################### end nwoutput  #######################")[0]
       data = data.lstrip()
       #data = data.strip()
       #ldata = data.split("\n")
       #data = ''
       #for ll in ldata[1:]:
       #   data += ll + "\n"
       #data = data.lstrip()

       if ("id=" in esmiles0):
          pname = "nwchem-" + esmiles0.split("id=")[1]
          fname = pname + '.out'
       else:
          fname = "nwchem-xxxx.out"
       with open(chemdbdir + "/" + fname,'w') as ff:
          ff.write(data)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> nwoutput_download failed </html>"
       return data

    return send_from_directory(directory='chemdb_hold', filename=fname,as_attachment=True)



@app.route('/api/nwinput/<esmiles0>', methods=['GET'])
def get_nwinput(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("nwinput: " + esmiles0 + " :nwinput\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### fetch the input deck from htmlfile ###
       with open(htmlfile,'r') as ff: data = ff.read()
       data = data.split("##################### start nwinput #######################")[1]
       data = data.split("##################### end nwinput   #######################")[0]
       html = "<html>\n"
       html += ArrowsHeader
       html += "<pre style=\"font-size:1.0em;color:black\">\n"
       html += data
       html += "</pre> </html>"
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> nwinput failed </html>"

    return  data



@app.route('/api/nwdatafile/<esmiles0>', methods=['GET'])
def get_nwdatafile(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("nwdatafile: " + esmiles0 + " :nwdatafile\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### fetch the input deck from htmlfile ###
       with open(htmlfile,'r') as ff: data = ff.read()
       data = data.split("##################### start nwdatafile #######################")[1]
       data = data.split("##################### end nwdatafile   #######################")[0]
       html = "<html>\n"
       html += ArrowsHeader
       html += "<pre style=\"font-size:1.0em;color:black\">\n"
       html += data
       html += "</pre> </html>"
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> nwdatafile failed </html>"

    return  data


@app.route('/api/nwdatafile_download/<esmiles0>', methods=['GET'])
def get_nwdatafile_download(esmiles0):
    global namecount
    name = "tmp/molecule%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("nwdatafile: " + esmiles0 + " :nwdatafile\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### fetch the input deck from htmlfile ###
       with open(htmlfile,'r') as ff: data = ff.read()
       data = data.split("##################### start nwdatafile #######################")[1]
       data = data.split("##################### end nwdatafile   #######################")[0]
       data = data.strip()
       ldata = data.split("\n")
       data = ''
       for ll in ldata[1:]:
          data += ll + "\n"
       data = data.lstrip()

       myid = ''
       if ('id=' in esmiles0):  myid = esmiles0.split('id=')[1].split()[0]

       gname = esmiles0.split()[1]
       pname = gname.split('.')[0]
       sname = gname.split('.')[1].split('-')[0]
       if "yaml" in sname: pname += myid
       fname = pname + '.' + sname
       with open(chemdbdir + "/" + fname,'w') as ff: 
          ff.write(data)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> nwdatafile_download failed </html>"
       return data

    return send_from_directory(directory='chemdb_hold', filename=fname,as_attachment=True)





@app.route('/api/reaction/<path:esmiles0>', methods=['GET'])
def get_reaction(esmiles0):
    global namecount
    name = "tmp/reaction%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    has_parsing = False
    parsing1 = ""
    try:

       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("!",'#')
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       if (("parse_output{" in esmiles0) and ("}" in esmiles0)):
          parsing1 = esmiles0.split("parse_output{")[1].split("}")[0]
          esmiles0 = esmiles0.replace("parse_output{"+parsing1+"}","")
          parsing1 = parsing1.strip()
          has_parsing = True

       machines0 = ''
       if "submitmachines{" in esmiles0:
          msg2 = esmiles0.split("submitmachines{")
          msg3 = msg2[1].split("}")[0]
          esmiles0 = esmiles0.replace("submitmachines{"+msg3+"}","")
          machines0 = msg3.strip()
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/reactiontmp-%d.txt" % ddrand
       outfile   = wrkdir + "/reactiontmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/reactiontmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          if (machines0!=''): ff.write("submitmachines: " + machines0 + "  :submitmachines\n")
          if (has_parsing):
             ff.write("reaction: " + esmiles0 + " :reaction useascii\n")
          else:
             ff.write("reaction: " + esmiles0 + " :reaction usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       if (has_parsing) or ("useascii" in esmiles0):
          data = html
       else:
          html = resolve_images(result,html)
          with open(htmlfile1,'w') as ff: ff.write(html)
          #print "rendering name=",name
          data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> reaction failed </html>"


    if (parsing1!=""): data = parse_output("reaction",parsing1,data)

    return  data



@app.route('/api/reactionpath/<esmiles0>', methods=['GET'])
def get_reactionpath(esmiles0):
    global namecount
    name = "tmp/reaction%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:

       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       esmiles0  = esmiles0.replace("==>",'-->')
       machines0 = ''
       if "submitmachines{" in esmiles0:
          msg2 = esmiles0.split("submitmachines{")
          msg3 = msg2[1].split("}")[0]
          esmiles0 = esmiles0.replace("submitmachines{"+msg3+"}","")
          machines0 = msg3.strip()
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/reactiontmp-%d.txt" % ddrand
       outfile   = wrkdir + "/reactiontmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/reactiontmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          if (machines0!=''): ff.write("submitmachines: " + machines0 + "  :submitmachines\n")
          ff.write("reactionpath: " + esmiles0 + " :reactionpath usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> reactionpath failed </html>"

    return  data





@app.route('/api/predict/<esmiles0>', methods=['GET'])
def get_predict(esmiles0):
    global namecount
    name = "tmp/reaction%d.html" % namecount
    namecount += 1

    increment_apivisited()
    clean_directories()

    try:

       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/reactiontmp-%d.txt" % ddrand
       outfile   = wrkdir + "/reactiontmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/reactiontmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          ff.write("predict: " + esmiles0 + " :predict   usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       ### resolve image files in html ###
       with open(htmlfile,'r') as ff: html = ff.read()
       html = resolve_images(result,html)
       with open(htmlfile1,'w') as ff: ff.write(html)

       #print "rendering name=",name
       data =  render_template(name)

       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> predict failed </html>"

    return  data



@app.route('/api/input_deck/<esmiles0>', methods=['GET'])
def get_input_deck(esmiles0):
    global namecount
    name = "tmp/reaction%d.html" % namecount
    namecount += 1
    try:
       increment_apivisited()
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       esmiles0 = esmiles0.replace("%2F",'/')
       esmiles0 = addspaces_reaction(esmiles0.strip())
       esmiles0 = parsetosmiles(esmiles0)
       cmd7 = tnt_submit + '\"' + esmiles0 + '\"'
       #data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       data = subprocess.check_output(cmd7,shell=True).decode("utf-8")
       #print "- input_deck: esmiles=",esmiles0
       if len(data) == 0: data=esmiles0 + " not generated\n"

       htmlfile1 = templatedir + "/"+name

       html = "<html>\n" 
       html += ArrowsHeader
       html += "<pre style=\"font-size:1.0em;color:black\">\n"
       html += data
       html += "</pre> </html>"
       with open(htmlfile1,'w') as ff: ff.write(html)
       data =  render_template(name)
    except:
       data = "Input generation failed\n"
    return data

@app.route('/api/crystal_input/<ocd0>', methods=['GET'])
def get_crystal_input_deck(ocd0):
    global namecount
    name = "tmp/reaction%d.html" % namecount
    namecount += 1
    try:
       ocd0 = ocd0.replace("\"",'')
       ocd0 = ocd0.replace("\'",'')
       cmd7 = cifocd_gennw +  ocd0 
       data = subprocess.check_output(cmd7,shell=True).decode("utf-8")
       if len(data) == 0: data=ocd0 + " not generated\n"

       htmlfile1 = templatedir + "/"+name

       html = "<html>\n" 
       html += ArrowsHeader
       html += "<pre style=\"font-size:1.0em;color:black\">\n"
       html += data
       html += "</pre> </html>"
       with open(htmlfile1,'w') as ff: ff.write(html)
       data =  render_template(name)
    except:
       data = "Input generation failed\n"
    return data




@app.route('/api/calculation/', methods=['GET'])
def get_calculation():
   try:
      cmd8 = chemdb_fetch_esmiles5 + '-c'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "calculations not found\n"
   return calcs


############################ queue_nwchem3 ###############################

@app.route('/api/queue_nwchem3/', methods=['GET'])
def list_queue_nwchem3():
   try:
      increment_apivisited()
      cmd8 = queue_nwchem3
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   return html


############################ queue        ###############################

@app.route('/api/queue/', methods=['GET'])
def list_queue():
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue + '-l'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data

@app.route('/api/queue_html/', methods=['GET'])
def list_queue_html():
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue + '-l'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   for ln in calcs.split("\n"):
      ss = ln.split()
      if (len(ss)==0):
         html += ln + "\n"
      elif ss[0].isdigit():
         restln = ln.split(ss[0])[1]
         link   = ARROWS_API_HOME + "queue_view/"+ss[0]
         hlink  = "<a href=\"" + link + "\">%s</a>" % ss[0]
         nspace = 11-len(ss[0])
         html += " " * nspace
         html += hlink + restln + "\n"
      else:
         html += ln + "\n"
   #html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data


@app.route('/api/queue_submit/', methods=['GET'])
def submit_queue():
   try:
      increment_apivisited()
      cmd8 = chemdb_queue + '-s'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   return html


@app.route('/api/queue_reset/<esmiles>', methods=['GET'])
def add_reset(esmiles):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      esmiles = esmiles.replace("\"",'')
      esmiles = esmiles.replace("\'",'')
      esmiles = esmiles.replace("%2F",'/')
      if ("M" in esmiles):
         cmd8 = chemdb_queue + '-m ' + '\"' +  esmiles + '\"'
      else:
         cmd8 = chemdb_queue + '-r ' + '\"' +  esmiles + '\"'
      #result = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      result = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      result = "queue_reset = " + esmiles + " was not reset on arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += result
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data


@app.route('/api/queue_delete/<esmiles>', methods=['GET'])
def add_delete(esmiles):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      esmiles = esmiles.replace("\"",'')
      esmiles = esmiles.replace("\'",'')
      esmiles = esmiles.replace("%2F",'/')
      cmd8 = chemdb_queue + '-d ' + '\"' +  esmiles + '\"'
      #result = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      result = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      result = "queue_delete = " + esmiles + " was not removed from arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += result
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data


@app.route('/api/queue_add/<esmiles>', methods=['GET'])
def add_queue(esmiles):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      esmiles = esmiles.replace("\"",'')
      esmiles = esmiles.replace("\'",'')
      esmiles = esmiles.replace("%2F",'/')
      cmd8 = chemdb_queue + '-a ' + '\"' +  esmiles + '\"'
      #result = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      result = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      result = "queue_add = " + esmiles + " was not added to arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += result
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data



@app.route('/api/queue_fetch/<jobid>', methods=['GET'])
def fetch_queue(jobid):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue + '-f ' + jobid
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data


@app.route('/api/queue_view/<jobid>', methods=['GET'])
def view_queue(jobid):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue + '-q ' + jobid
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   if "START NWCHEM INPUT DECK - NWJOB" in calcs:
      queuenumber = calcs.split("START NWCHEM INPUT DECK - NWJOB")[1].split("#")[0].strip()
   else:
      queuenumber = "unknown"

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   if queuenumber!="unknown":
      link   = ARROWS_API_HOME + "queue_html"
      hlink  = "Arrows <a href=\"" + link + "\">queue</a> entry:" + queuenumber
      html += hlink + "\n"
      html += nwinput2jsmol("0x8c0101",calcs)
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data =  render_template(name)

   return data


@app.route('/api/eric_view/<path:input_data>', methods=['GET'])
def eric_queue(input_data):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_eric + '\"' + input_data + '\"'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"


   if ("DOWNLOAD FILE:" in calcs) and (":DOWNLOAD FILE" in calcs):
      dname = input_data.split("download=")[1].split()[0].split("/")[-1]
      data = calcs.split("DOWNLOAD FILE:")[1].split(":DOWNLOAD FILE")[0].strip()
      ddfile = chemdbdir + "/"+dname
      with open(ddfile,"w") as ff:
         ff.write(data)
      zname = dname +".zip"
      zipf = zipfile.ZipFile("chemdb_hold/"+zname,'w', zipfile.ZIP_DEFLATED)
      zipf.write(ddfile,arcname=dname)
      zipf.close()
      return send_from_directory(directory='chemdb_hold', filename=zname,as_attachment=True)
   elif ("RAW_DATA:" in calcs) and (":RAW_DATA" in calcs):
      data = calcs.split("RAW_DATA:")[1].split(":RAW_DATA")[0].strip()
      return data
   else:
      htmlfile1 = templatedir + "/"+name

      #if "START NWCHEM INPUT DECK - NWJOB" in calcs:
      #   queuenumber = calcs.split("START NWCHEM INPUT DECK - NWJOB")[1].split("#")[0].strip()
      #else:
      #   queuenumber = "unknown"

      html = "<html>\n"
      html += ArrowsHeader
      html += "<pre style=\"font-size:2.0em;color:black\">\n"
      html += "input_data = %s\n" % input_data
      #if queuenumber!="unknown":
      #   link   = "https://arrows.emsl.pnnl.gov/api/queue_html"
      #   hlink  = "Arrows <a href=\"" + link + "\">queue</a> entry:" + queuenumber
      #   html += hlink + "\n"
      #   html += nwinput2jsmol("0x8c0101",calcs)
      #html +=  calcs
      #html += "</pre> </html>"

      with open(htmlfile1,'w') as ff: 
         ff.write(html)
         ff.write(calcs+"\n")
         ff.write("</pre> </html>")
      data =  render_template(name)

      return data




@app.route('/api/submit_output/<datafiles>', methods=['GET'])
def submit_output_deck(datafiles):
   #
   increment_apivisited()
   datafiles = datafiles.replace("\"",'')
   datafiles = datafiles.replace("\'",'')

   #tt1 = time.localtime()
   #dd1 = "-%d-%d-%d-%d-%d-%d" % (tt1[0],tt1[1],tt1[2],tt1[3],tt1[4],tt1[5])
   ddrand = random.randint(0,999999)
   dd1 = "-%d" % (ddrand)

   # copy data to chemdbdir and find nwoutfile and datafiles ####
   nwoutfile = ''
   nwoutfile0 = ''
   string_of_datafiles = ''
   string_of_datafiles0 = ''
   for filename in datafiles.split():
      nwfilename  = UPLOAD_FOLDER + filename[filename.rfind('/')+1:]
      nwfilename1 = chemdbdir + "/" + filename[filename.rfind('/')+1:]+dd1
      nwfilename1 = nwfilename1.replace(",","-")
      if os.path.exists(nwfilename):
         ### copy data to chemdbdir ###
         with open(nwfilename, 'r') as ff: tdata = ff.read()
         with open(nwfilename1,'w') as ff: ff.write(tdata)

         ### look for nwout file  or datafile ###
         if ('.out' in filename) or ('.nwo' in filename):
            nwoutfile  = nwfilename1
            nwoutfile0 = filename
         else:
            string_of_datafiles  += nwfilename1 + " "
            string_of_datafiles0 += filename  + " "
   string_of_datafiles  = string_of_datafiles.strip()
   string_of_datafiles0 = string_of_datafiles0.strip()

   #### call chemdb_queue ###
   if nwoutfile != '':
      msg = "Submited " + nwoutfile0 
      cmd1 = chemdb_queue + "-w " +  nwoutfile 
      if string_of_datafiles!='':
         cmd1 +=  " -z \""+string_of_datafiles+"\""
         msg  += " with the following extra datafiles=" + string_of_datafiles0

      result = subprocess.check_output(cmd1,shell=True,stderr=subprocess.STDOUT).decode("utf-8")

   else:
      msg = "Nothing was submited"

   #### clean the upload directory ####
   clean_upload_directory()

   return msg
      



@app.route('/api/upload/', methods=['GET','POST'])
def index():
    #print "i am here", request
    if request.method == 'POST':
        #print "after post"
        file = request.files['file']
        #print "FILE=",file
        #print "file.filename=",file.filename, " file=",file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))


############################ queue        ###############################

############################ queue_nwchem ###############################

@app.route('/api/queue_nwchem/', methods=['GET'])
def list_queue_nwchem():
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + '-l'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"
  
   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data


@app.route('/api/queue_nwchem_html/', methods=['GET'])
def list_queue_nwchem_html():
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + '-l'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   for ln in calcs.split("\n"):
      ss = ln.split()
      if (len(ss)==0):
         html +=  ln + "\n"
      elif ss[0].isdigit():
         restln = " " + ln.strip().split(' ',1)[1]
         try:
            stime = ((time.time() - evalnum(restln.split()[-1])) > 2592000.0)  # approximately 30 days
         except:
            stime = True
         stime = stime or ("aerosol" in ln)
         isfinished = "yes" in restln.split()[1]
         link   = ARROWS_API_HOME + "queue_nwchem_view/"+ss[0]
         zzip   = ARROWS_API_HOME + "queue_nwchem_zip/"+ss[0]
         dentr  = ARROWS_API_HOME + "queue_nwchem_delete/"+ss[0]
         hlink  = "<a href=\"" + link + "\">%s</a> " % ss[0]
         zlink  = "<a href=\"" + zzip + "\">%s</a>" % ("(zip)")
         zlink2 = "     "
         dlink  = "<a href=\"" + dentr + "\">%s</a> " % ("(remove)")
         dlink2 = "(remove) "
         nspace = 11-len(ss[0])
         html += " " * (nspace)
         if isfinished:
            if (stime):
               html += hlink + zlink + dlink + restln + "\n"
            else:
               html += hlink + zlink + dlink2 + restln + "\n"
         else:
            html += hlink + zlink2 + dlink2 + restln + "\n"
      elif "queue_entry" in ln:
         restln = ln.split("queue_entry")[1]
         html += "      queue_entry         " + restln + "\n"
      else:
         html += ln + "\n"
   #html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data


@app.route('/api/queue_nwchem_check/<qname>', methods=['GET'])
def list_queue_nwchem_check(qname):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + '-l'
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "arrows queue not found\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   if ("qsharp" in qname):
      html += ArrowsHeader2
   else:
      html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   for ln in calcs.split("\n"):
      ss = ln.split()
      if (len(ss)==0):
         html +=  ln + "\n"
      elif ss[0].isdigit():
         if (qname in ss[6]):
            restln = ln.split(ss[0])[1]
            try:
               stime = ((time.time() - evalnum(restln.split()[-1])) >  2592000.0)  #30 days
            except:
               stime = True
            stime = stime or ("aerosol" in ln)
            isfinished = "yes" in restln.split()[1]
            link   = "https://arrows.emsl.pnnl.gov/api/queue_nwchem_view/"+ss[0]
            zzip   = "https://arrows.emsl.pnnl.gov/api/queue_nwchem_zip/"+ss[0]
            dentr  = "https://arrows.emsl.pnnl.gov/api/queue_nwchem_delete/"+ss[0]
            hlink  = "<a href=\"" + link + "\">%s</a> " % ss[0]
            zlink  = "<a href=\"" + zzip + "\">%s</a>" % ("(zip)")
            zlink2 = "     "
            dlink  = "<a href=\"" + dentr + "\">%s</a> " % ("(remove)")
            dlink2 = "(remove) "
            nspace = 11-len(ss[0])
            html += " " * (nspace)
            if isfinished:
               if (stime):
                  html += hlink + zlink + dlink + restln + "\n"
               else:
                  html += hlink + zlink + dlink2 + restln + "\n"
            else:
               html += hlink + zlink2 + dlink2 + restln + "\n"
      elif "queue_entry" in ln:
         restln = ln.split("queue_entry")[1]
         html += "      queue_entry         " + restln + "\n"
      else:
         html += ln + "\n"
   #html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data



@app.route('/api/queue_nwchem_add/<filename>', methods=['GET'])
def add_queue_nwchem(filename):
   increment_apivisited()
   #print "filename=",filename
   filename = filename.replace("\"",'')
   filename = filename.replace("\'",'')

   nwfilename  = UPLOAD_FOLDER + filename[filename.rfind('/')+1:]

   #### call chemdb_queue ###
   if nwfilename != '':
      msg = "Submited " + nwfilename
      cmd1 = chemdb_queue_nwchem + "-a " +  nwfilename
      print("cmd1=",cmd1)
      result = subprocess.check_output(cmd1,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      print("result=",result)
      qqnum = result.split("QUEUE_ENTRY:")[1].split(":QUEUE_ENTRY")[0]
      msg += " - queue_entry = " + qqnum + "\n"

   else:
      msg = "Nothing was submited"

   #### clean the upload directory ####
   clean_upload_directory()

   return msg


@app.route('/api/queue_nwchem_fetch/<jobid>', methods=['GET'])
def fetch_queue_nwchem(jobid):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + '-f ' + jobid
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"

   try:
      if ("OUTPUT AVAILABLE!" in calcs) and ("EAP_PICKLE::" not in calcs):
         nwoutfile = calcs.split("nwoutfile       =")[1].split("\n")[0].strip()
         extra_datafiles = calcs.split("extra_datafiles =")[1].split("\n")[0]
         with open(nwoutfile,'r') as ff:
            calcs += ff.read()
         for dfile in extra_datafiles.split():
            calcs += "\n=================NEXT FILE: " + dfile + ":NEXT FILE===================\n"
            with open(dfile,'r') as ff: calcs += ff.read()
   except:
      print("LOOKing for bad files!")

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data


@app.route('/api/queue_nwchem_view/<jobid>', methods=['GET'])
def view_queue_nwchemw(jobid):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + ' -q ' + jobid
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"

   try:
      if ("OUTPUT AVAILABLE!" in calcs) and ("EAP_PICKLE::" not in calcs):
         nwoutfile = calcs.split("nwoutfile       =")[1].split("\n")[0].strip()
         extra_datafiles = calcs.split("extra_datafiles =")[1].split("\n")[0]
         with open(nwoutfile,'r') as ff:
            calcs += ff.read()
         for dfile in extra_datafiles.split():
            calcs += "\n=================NEXT FILE: " + dfile + ":NEXT FILE===================\n"
            with open(dfile,'r') as ff: calcs += ff.read()
   except:
      print("LOOKing for bad files!")

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data


@app.route('/api/queue_nwchem_zip/<jobid>', methods=['GET'])
def zip_queue_nwchem(jobid):
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + ' -f ' + jobid
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"

   try:
      if ("OUTPUT AVAILABLE!" in calcs) and ("EAP_PICKLE::" not in calcs):
         nwoutfile = calcs.split("nwoutfile       =")[1].split("\n")[0].strip()
         extra_datafiles = calcs.split("extra_datafiles =")[1].split("\n")[0]

         #### look for yaml daa ####
         try:
            with open(nwoutfile, 'r') as ff: tdata = ff.read()
            if ("begin_two_electron_integrals" in tdata):
               ddrand = random.randint(0,999999)
               dd1 = "-%d" % (ddrand)
               myyamlfile = chemdbdir + "/" + "microsoft_qsharp_chem.yaml" + dd1
               matrix_elements = parse_matrix_elements(nwoutfile)
               if (len(matrix_elements)>0):
                  matrix_elements_blob = '\n' + '\n"$schema": https://raw.githubusercontent.com/Microsoft/Quantum/master/Chemistry/Schema/broombridge-0.1.schema.json\n\n'
                  matrix_elements_blob += yaml.dump(matrix_elements)
                  with open(myyamlfile,'w') as ff:
                     ff.write(matrix_elements_blob)
                  extra_datafiles += " " + myyamlfile
         except:
            print("Failed in YAML Generation")
         #calcs += send_from_directory(directory='chemdb_hold', filename=nwoutfile.split('/')[-1],as_attachment=True)
         #calcs += send_from_directory(filename=nwoutfile,as_attachment=True)
         #with open(nwoutfile,'r') as ff:
         #   calcs += ff.read()
         #for dfile in extra_datafiles.split():
         #   calcs += "\n=================NEXT FILE: " + dfile + ":NEXT FILE===================\n"
         #   with open(dfile,'r') as ff: calcs += ff.read()
         zipf = zipfile.ZipFile("chemdb_hold/"+jobid+'.zip','w', zipfile.ZIP_DEFLATED)
         nwfile = "-".join(nwoutfile.split("/")[-1].split("-")[0:-1])
         zipf.write("chemdb_hold/"+nwoutfile.split("/")[-1],"chemdb_hold_"+jobid+"/" + nwfile)
         for dfile in extra_datafiles.split():
            nwfile = "-".join(dfile.split("/")[-1].split("-")[0:-1])
            zipf.write("chemdb_hold/"+dfile.split('/')[-1],"chemdb_hold_"+jobid+"/"+nwfile)
         zipf.close()
   except:
      print("LOOKing for bad files!")

   #html = "<html>\n"
   #html += ArrowsHeader
   #html += calcs
   #html += "</html>"
   fname = jobid + ".zip"

   return send_from_directory(directory='chemdb_hold', filename=fname,as_attachment=True)





@app.route('/api/queue_nwchem_delete/<jobid>', methods=['GET'])
def delete_queue_nwchem(jobid):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      cmd8 = chemdb_queue_nwchem + '-d ' + jobid
      #calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      calcs = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      calcs = "queue_entry = " + jobid + " was not found in arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += calcs
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data

@app.route('/api/queue_nwchem_reset/<esmiles>', methods=['GET'])
def queue_nwchem_add_reset(esmiles):
   global namecount
   name = "tmp/molecule%d.html" % namecount
   namecount += 1
   try:
      increment_apivisited()
      esmiles = esmiles.replace("\"",'')
      esmiles = esmiles.replace("\'",'')
      esmiles = esmiles.replace("%2F",'/')
      cmd8 = chemdb_queue_nwchem + '-r ' + '\"' +  esmiles + '\"'
      #result = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      result = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      result = "queue_nwchem_reset = " + esmiles + " was not added to arrows queue.\n"

   htmlfile1 = templatedir + "/"+name

   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += result
   html += "</pre> </html>"

   with open(htmlfile1,'w') as ff: ff.write(html)
   data = render_template(name)
   return data





@app.route('/api/download_datafile/<datafile>', methods=['GET'])
def download_datafiler0(datafile):
   increment_apivisited()
   datafile = datafile.replace("\"",'')
   datafile = datafile.replace("\'",'')
   filename = datafile
   ddfile = filename[filename.rfind('/')+1:]
   return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)


@app.route('/api/submit_output_nwchem/<datafiles>', methods=['GET'])
def submit_output_nwchem_deck(datafiles):
   #
   print("datafiles=",datafiles)
   increment_apivisited()
   datafiles = datafiles.replace("\"",'')
   datafiles = datafiles.replace("\'",'')

   print("datafiles2=",datafiles)


   #tt1 = time.localtime()
   #dd1 = "-%d-%d-%d-%d-%d-%d" % (tt1[0],tt1[1],tt1[2],tt1[3],tt1[4],tt1[5])
   ddrand = random.randint(0,999999)
   dd1 = "-%d" % (ddrand)

   #### copy data to chemdbdir and find nwoutfile and datafiles ####
   nwoutfile = ''
   nwoutfile0 = ''
   string_of_datafiles = ''
   string_of_datafiles0 = ''
   for filename in datafiles.split():
      nwfilename  = UPLOAD_FOLDER + filename[filename.rfind('/')+1:]
      nwfilename1 = chemdbdir + "/" + filename[filename.rfind('/')+1:]+dd1

      #nwfilename1 = chemdbdir + "/" + filename[filename.rfind('/')+1:]
      #if "." in nwfilename1:
      #   ppre  = ".".join(nwfilename1.split(".")[0:-1])
      #   ppost = nwfilename1.split(".")[-1]
      #   nwfilename1 = ppre + dd + "." + ppost
      #else:
      #   nwfilename1 = nwfilename1+dd1

      nwfilename1 = nwfilename1.replace(",","-")
      print("FILENAME,nwfilename=",filename,nwfilename,nwfilename1)
      if os.path.exists(nwfilename):
         ### copy data to chemdbdir ###
         with open(nwfilename, 'r') as ff: tdata = ff.read()
         with open(nwfilename1,'w') as ff: ff.write(tdata)

         ### look for nwout file  or datafile ###
         if ('.out' in filename) or ('.nwo' in filename):
            nwoutfile  = nwfilename1
            nwoutfile0 = filename

            ### check for yaml ###
            if ("begin_two_electron_integrals" in tdata):
               myyamlfile = chemdbdir + "/" + "microsoft_qsharp_chem.yaml" + dd1
               string_of_datafiles += " " + myyamlfile 
               matrix_elements = parse_matrix_elements(nwfilename)
               if (len(matrix_elements)>0):
                  matrix_elements_blob = '\n' + '\n"$schema": https://raw.githubusercontent.com/Microsoft/Quantum/master/Chemistry/Schema/broombridge-0.1.schema.json\n\n'
                  matrix_elements_blob += yaml.dump(matrix_elements)
                  with open(myyamlfile,'w') as ff:
                     ff.write(matrix_elements_blob)

         else:
            string_of_datafiles  += nwfilename1 + " "
            string_of_datafiles0 += filename  + " "
   string_of_datafiles  = string_of_datafiles.strip()
   string_of_datafiles0 = string_of_datafiles0.strip()

  #### call chemdb_queue ###
   if nwoutfile != '':
      msg = "Submited " + nwoutfile0
      cmd1 = chemdb_queue_nwchem + "-w " +  nwoutfile
      if string_of_datafiles!='':
         cmd1 +=  " -z \""+string_of_datafiles+"\""
         msg  += " with the following extra datafiles=" + string_of_datafiles0

      print("cmd1=",cmd1)
      result = subprocess.check_output(cmd1,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      print("upload RESULT=",result)

   else:
      msg = "Nothing was submited"

   #### clean the upload directory ####
   clean_upload_directory()

   return msg




############################ queue_nwchem ###############################





@app.route('/api/')
def arrows_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("JSME-arrows.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/', methods=['POST'])
def arrows_draw_post():

    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    #if "-->" in text:
    #   reaction = text
    #   return get_reaction(reaction)
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()):
       nrows = text.lower().split("list all esmiles")[1].split()
       if (len(nrows)>0):
          nrows =nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("listallesmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows =nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("list all reactions"  in text.lower()) or ("listallreactions"  in text.lower()):
       return get_listallreactions()
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)

    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text



@app.route('/api/rxn')
def arrows_reaction_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("JSME-arrows-rxn.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/rxn', methods=['POST'])
def arrows_reaction_draw_post():

    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    #if "-->" in text:
    #   reaction = text
    #   return get_reaction(reaction)
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()) or ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("esmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows = nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)

    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text


@app.route('/api/3dbuilder')
def arrows_3dbuilder_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("Jmol-arrows.html",calculations=calcs,moleculecalculations=molcalcs,visits=avisits)


@app.route('/api/3dbuilder', methods=['POST'])
def arrows_3dbuilder_draw_post():

    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    #if "-->" in text:
    #   reaction = text
    #   return get_reaction(reaction)
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()) or ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("esmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows = nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("list all reactions"  in text.lower()) or ("listallreactions"  in text.lower()):
       return get_listallreactions()
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)


    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text


@app.route('/api/qsharp_chem')
def arrows_qsharp_chem_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("Qsharp-chem-arrows.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)


@app.route('/api/qsharp_chem', methods=['POST'])
def arrows_qsharp_chem_draw_post():

    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    #if "-->" in text:
    #   reaction = text
    #   return get_reaction(reaction)
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()) or ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("esmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows = nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("list all reactions"  in text.lower()) or ("listallreactions"  in text.lower()):
       return get_listallreactions()
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)

    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text


@app.route('/api/expert')
def arrows_expert_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("Expert-arrows.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)


@app.route('/api/expert', methods=['POST'])
def arrows_expert_draw_post():

    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    #if "-->" in text:
    #   reaction = text
    #   return get_reaction(reaction)
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()) or ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("esmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows = nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("list all reactions"  in text.lower()) or ("listallreactions"  in text.lower()):
       return get_listallreactions()
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)

    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text





@app.route('/api/periodic')
def arrows_periodic_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("Periodic-arrows.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/periodic', methods=['POST'])
def arrows_periodic_draw_post():

    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    #if "-->" in text:
    #   reaction = text
    #   return get_reaction(reaction)
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()) or ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("esmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows = nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("list all reactions"  in text.lower()) or ("listallreactions"  in text.lower()):
       return get_listallreactions()
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)

    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text




#############################
#                           #
#       parsing_text        #
#                           #
#############################
def parsing_text():
    if "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif "predict for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_predict(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("nwinput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwinput(esmiles)
       #return get_input_deck(esmiles)
    elif ("crystal input for" in text.lower()) or ("ocd for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       ocd = text2.split('for')[1]
       return get_crystal_input_deck(ocd)
    elif ("output deck for" in text.lower()) or ("outputdeck for" in text.lower()) or ("nwoutput for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nwoutput(esmiles)
    elif "submitesmiles for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_submitesmiles(esmiles)
    elif "xyz for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_xyz(esmiles)
    elif "json for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_esmiles(esmiles)
    elif "frequency for" in text.lower():
       text2 = ireplace("FOR","for",text)
       idfnum = text2.split('for')[1]
       return get_frequency(idfnum)
    elif "smarts" in text.lower():
       text2  = ireplace("SMARTS","smarts",text)
       smarts = text2.split('smarts')[1]
       return get_smarts(smarts)
    elif ("list all esmiles"  in text.lower()) or ("listallesmiles"  in text.lower()):
       nrows = text.lower().split("esmiles")[1].split()[0]
       if (len(nrows)>0):
          nrows = nrows[0]
       else:
          nrows = ''
       return get_listallesmiles(nrows)
    elif ("list all reactions"  in text.lower()) or ("listallreactions"  in text.lower()):
       return get_listallreactions()
    elif ("queue_nwchem3" in text.lower()):
       return list_queue_nwchem3()
    elif ("queue_nwchem" in text.lower()):
       return list_queue_nwchem_html()
    elif ("queue" in text.lower()):
       return list_queue_html()
    elif ("download fetch_nwchem_input" in text.lower()):
       return send_from_directory(directory='programs', filename='fetch_nwchem_input.py',as_attachment=True)
    elif ("download upload_nwchem_outfiles" in text.lower()):
       return send_from_directory(directory='programs', filename='upload_nwchem_outfiles.py',as_attachment=True)
    elif ("download arrows_esmiles2xyz" in text.lower()):
       return send_from_directory(directory='programs', filename='arrows_esmiles2xyz.py',as_attachment=True)
    elif ("download ring.c" in text.lower()):
       return send_from_directory(directory='programs', filename='ring.c',as_attachment=True)

    elif ("download datafile" in text):
       filename = text.strip("download datafile").strip()
       ddfile = filename[filename.rfind('/')+1:]
       return send_from_directory(directory='chemdb_hold', filename=ddfile,as_attachment=True)

    elif ("==>" in text):
       reaction = text
       return get_reactionpath(reaction)

    elif ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_type" not in text) and ("reaction_indexes" not in text):
       reaction = text
       return get_reaction(reaction)

    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text


@app.route('/api/eugene')
def arrows_eugene_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("Eugene.html",calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/eugene', methods=['POST'])
def arrows_eugene_draw_post():
    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    return parsing_text(text)


@app.route('/api/aerosol')
def arrows_aerosol_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("emsl-aerosols.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/aerosol', methods=['POST'])
def arrows_aerosol_draw_post():
    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    return parsing_text(text)

@app.route('/api/aerosol-eric')
def arrows_aerosol_eric_draw_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("emsl-aerosols-eric.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/aerosol-eric', methods=['POST'])
def arrows_aerosol_eric_draw_post():
    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    return parsing_text(text)







@app.route('/api/arrows_input/')
def arrows_form():
   increment_apivisited()
   return render_template("arrows-input.html")

@app.route('/api/arrows_input/', methods=['POST'])
def arrows_post():

    text = request.form['text']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    if ("-->" in text) and ("reaction_hash" not in text) and ("reaction_genhash" not in text) and ("reaction_gamma" not in text):
       reaction = text
       return get_reaction(reaction)
    elif "nmr for" in text.lower():
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_nmr(esmiles)
    elif ("input deck for" in text.lower()) or ("inputdeck for" in text.lower()) or ("input_deck for" in text.lower()):
       text2 = ireplace("FOR","for",text)
       esmiles = text2.split('for')[1]
       return get_input_deck(esmiles)
    else:
       esmiles = text
       return get_molecule(esmiles)

    processed_text = "EMSL Arrows did not understand \"" + text + "\"."
    return processed_text



@app.route('/api/image_reset/<arrows_id>', methods=['GET'])
def image_reset(arrows_id):
   try:
      increment_apivisited()
      cmd8 = chemdb_image0 + arrows_id
      #result = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
      result = subprocess.check_output(cmd8,shell=True).decode("utf-8")
   except:
      result = "image_reset = " + arrows_id + " was not reset.\n"
   html = "<html>\n"
   html += ArrowsHeader
   html += "<pre style=\"font-size:1.0em;color:black\">\n"
   html += result
   html += "</pre> </html>"

   return html


@app.route('/api/genhash/<filename>', methods=['GET'])
def genhash_reaction(filename):
   increment_apivisited()
   reaction_hash = ''
    
   filename = filename.replace("\"",'')
   filename = filename.replace("\'",'')

   molfilename  = UPLOAD_FOLDER + filename[filename.rfind('/')+1:]

   #### call chemdb_balance_reaction ###
   if molfilename != '':
      try:
         time.sleep(0.1)
         with open(molfilename,'r') as ff:
            moldata = ff.read()
         print("genhash: moldata=",moldata)

         if ("reaction_genhash{" in moldata):
            reaction_genhash0 = moldata.split('reaction_genhash{')[1].split('}')[0].strip()
            cmd9 = chemdb_balance_reaction + "-x \"0 0 0 0 0 " + reaction_genhash0.replace("==>","-->") + "\""
            result9 = subprocess.check_output(cmd9,shell=True).decode("utf-8")
            if "bstringsall =" in result9:
               bstringsall = eval(result9.split("bstringsall = ")[1].split('\n')[0].strip())
               reaction_hash = bstringsall[0][3]
         elif  ("generate_bonding" in moldata) and ("reaction_type{" in moldata) and ("reaction_indexes{" in moldata):
            reaction_type    = moldata.split('reaction_type{')[1].split('}')[0].strip()
            reaction_indexes = moldata.split('reaction_indexes{')[1].split('}')[0].strip()
            cmd9 = chemdb_balance_reaction + "-c " + " \"" + reaction_indexes + "\" \"" + reaction_type + "\""
            result9 = subprocess.check_output(cmd9,shell=True).decode("utf-8")
            reaction_hash = result9
         elif  ("reaction_type{" in moldata) and ("reaction_indexes{" in moldata):
            reaction_type    = moldata.split('reaction_type{')[1].split('}')[0].strip()
            reaction_indexes = moldata.split('reaction_indexes{')[1].split('}')[0].strip()
            cmd9 = chemdb_balance_reaction + "-r " + molfilename + " \"" + reaction_indexes + "\" \"" + reaction_type + "\""
            result9 = subprocess.check_output(cmd9,shell=True).decode("utf-8")
            #reaction_hash = result9.split("rhash =")[1].split("\n")[0].strip()
            reaction_hash = result9
         elif ("reaction_hash{" in moldata):
            reaction_hash0 = moldata.split('reaction_hash{')[1].split('}')[0].strip()
            cmd9 = chemdb_balance_reaction + "-e " + molfilename + " \"" + reaction_hash0 + "\""
            result9 = subprocess.check_output(cmd9,shell=True).decode("utf-8")
            reaction_type    = reaction_hash0.split(":")[1]
            reaction_indexes = result9.split("reaction regular indexes=")[1].split("\n")[0]
            reaction_hash    = reaction_type + "\n" + reaction_indexes + "\n"
         else:
            reaction_hash = "reaction_hash not generated"
         #os.unlink(molfilename)
      except:
         reaction_hash = "reaction_genhash failed!"

   return reaction_hash




@app.route('/api/molecular_calculation/<filename>', methods=['GET'])
def run_molecular_calculation(filename):
   increment_apivisited()
   html = ''

   filename = filename.replace("\"",'')
   filename = filename.replace("\'",'')

   molfilename  = UPLOAD_FOLDER + filename[filename.rfind('/')+1:]

   #### call chemdb_molcalc - Not Finished! just run tnt_submit for now ###
   if molfilename != '':
      try:
         time.sleep(0.1)
         print("Running chemdb_molcalc, molfilename=",molfilename)
         cmd7 = chemdb_molcalc + molfilename
         print("HHHERAAA, cmd7=",cmd7)
         data = subprocess.check_output(cmd7,shell=True).decode("utf-8")
         if len(data) == 0: data = " chemdb_molcalc did not generate data\n"
         #html = "<html>\n"
         #html += ArrowsHeader
         html = "<pre style=\"font-size:1.0em;color:black\">\n"
         html += data
         html += "</pre>"
         #html += "</pre> </html>"

      except:
         html = "molecular_calculation failed!"

   return html




@app.route('/api/broombridge/<esmiles0>', methods=['GET'])
def get_broombridge(esmiles0):
    global namecount
    name = "molecule%d.html" % namecount
    namecount += 1

    hasjson = False
    if ("json" in esmiles0.lower()):
       esmiles0 = esmiles0.replace("json","")
       esmiles0 = esmiles0.replace("JSON","")
       hasjson = True

    if ("theory{qsharp_chem}" not in esmiles0.lower()):
       esmiles0  += " theory{qsharp_chem}"

    increment_apivisited()
    clean_directories()

    has_parsing = False
    parsing1 = ""
    try:
       ### run chemdb_fetch_reactions ###
       esmiles0  = esmiles0.replace("\"",'')
       esmiles0  = esmiles0.replace("\'",'')
       esmiles0  = esmiles0.replace("%2F",'/')
       machines0 = ''
       if "submitmachines{" in esmiles0:
          msg2 = esmiles0.split("submitmachines{")
          msg3 = msg2[1].split("}")[0]
          esmiles0 = esmiles0.replace("submitmachines{"+msg3+"}","")
          machines0 = msg3.strip()
       ddrand = random.randint(0,999999)
       inpfile   = wrkdir + "/moleculetmp-%d.txt" % ddrand
       outfile   = wrkdir + "/moleculetmp-%d.plain" % ddrand
       htmlfile  = wrkdir + "/moleculetmp-%d.html" % ddrand
       htmlfile1 = templatedir + "/"+name
       with open(inpfile,'w') as ff:
          if (machines0!=''): ff.write("submitmachines: " + machines0 + "  :submitmachines\n")
          if (has_parsing):
             ff.write("molecule: " + esmiles0 + " :molecule useascii\n")
          else:
             ff.write("molecule: " + esmiles0 + " :molecule usehtml5\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       #result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT).decode("utf-8")
       #print "CMD7=",cmd7
       result = subprocess.check_output(cmd7,shell=True).decode("utf-8")

       with open(htmlfile,'r') as ff: html = ff.read()
       if ("qsharp_chem.yaml" in html) and ("https://arrows.emsl.pnnl.gov/api/nwdatafile/%22id=" in html):
          myid = html.split("https://arrows.emsl.pnnl.gov/api/nwdatafile/%22")[1].split("%22")[0]
          fdata = get_nwdatafile(myid)
          mblob = ''
          found = False
          for ln in fdata.split("\n"):
             if "$schema" in ln:
                mblob = ln + "\n"
                found = True
             elif ("</pre>" in ln):
                found = False
             elif (found):
                mblob += ln + "\n"
          y=yaml.load(mblob)
          if (hasjson):
             data = Response(jsonify(y),mimetype='application/json')
          else:
             data = Response(yaml.dump(y),mimetype='text/yaml')
       else:
          ### resolve image files in html ###
          html = resolve_images(result,html)
          with open(htmlfile1,'w') as ff: ff.write(html)

          #print "rendering name=",name
          data =  render_template(name)


       try:
          os.unlink(inpfile)
          os.unlink(outfile)
          os.unlink(htmlfile)
       except Exception as e:
          print(e)

    except:
       data = "<html> broombridge failed </html>"

    return data



@app.route('/api/broombridge_queue/<jobid>', methods=['GET'])
def get_broombridge_queue(jobid):
   hasjson = False
   if ("json" in jobid.lower()):
      hasjson = True
      jobid = jobid.replace("json","").strip()
   data0 = view_queue_nwchemw(jobid)
   try:
      if ("microsoft_qsharp_chem.yaml" in data0):
         found = False
         for ln in data0.split("\n"):
            if ("https://raw.githubusercontent.com/Microsoft/Quantum/master/Chemistry/Schema/broombridge-0.1.schema.json" in ln):
               found = True
               mblob = ln + "\n"
            elif ("</pre>" in ln) or ("=================NEXT FILE:" in ln):
               found = False
            elif found:
               mblob += ln + "\n"
         y=yaml.load(mblob)
         if (hasjson):
            data = Response(jsonify(y),mimetype='application/json')
         else:
            data = Response(yaml.dump(y),mimetype='text/yaml')
   except:
      data = "<html> broombridge_queue failed </html>"

   return data


@app.route('/api/eric_input/')
def eric_form():
   increment_apivisited()
   return render_template("eric-input.html",arrows_api=ARROWS_API_HOME)

@app.route('/api/eric_input/', methods=['POST'])
def eric_form_post():
    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    return parsing_text(text)


@app.route('/api/eric_input2/')
def eric_form2():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   #return render_template("eric-input2.html")
   return render_template("eric-input2.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/eric_input2/', methods=['POST'])
def eric_form2_post():
    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    return parsing_text(text)


@app.route('/api/eric_input4/')
def eric_form4():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   return render_template("eric-input4.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)

@app.route('/api/eric_input4/', methods=['POST'])
def eric_form4_post():
    text = request.form['smi']
    text = text.replace("\"","")
    text =  " ".join(text.split())
    return parsing_text(text)


@app.route('/api/reaction_prediction/')
def dagrereaction_form():
   increment_apivisited()
   calcs = arrowsjobsrun()
   molcalcs = calculationscount()
   avisits = apivisited()
   #return render_template("eric-input2.html")
   return render_template("dagre-rxn.html",arrows_api=ARROWS_API_HOME,calculations=calcs,moleculecalculations=molcalcs,visits=avisits)



if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True,host='0.0.0.0', threaded=True)
