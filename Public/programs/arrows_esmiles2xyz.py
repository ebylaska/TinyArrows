#!/usr/local/bin/python

# This program can be used to fetch an xyz file from the arrows database.
# Example uses -
# python arrows_esmiles2xyz  prozac prozac.xyz
# python arrows_esmiles2xyz  TNT TNT.xyz
# python arrows_esmiles2xyz  "CC(O)"  alcohol.xyz
# python arrows_esmiles2xyz  "CC(O)"  alcohol.xyz
# python arrows_esmiles2xyz  "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"  alcohol.xyz
# python arrows_esmiles2xyz  "pubchem=702"  alcohol.xyz
# python arrows_esmiles2xyz  "cid=702"  alcohol.xyz
# python arrows_esmiles2xyz  "chemspider=682"  alcohol.xyz
# python arrows_esmiles2xyz  "csid=682"  alcohol.xyz
# python arrows_esmiles2xyz  "cas=64-17-5"  alcohol.xyz
# python arrows_esmiles2xyz  "kegg=C00469"  alcohol.xyz
# python arrows_esmiles2xyz  "kegg=D00068"  alcohol.xyz
#
# with jmol
# python arrows_esmiles2xyz -j prozac prozac.xyz
# python arrows_esmiles2xyz -j TNT TNT.xyz
# python arrows_esmiles2xyz -j "CC(O)"  alcohol.xyz
# ....
# 


import sys,os,time,getopt,requests,urlib2
import json

#################### machine specifics - change this to the location of your jmol ######################
jmol     = "/Users/bylaska/bin/jmol "
#################### machine specifics - change this to the location of your jmol ######################

#### geturlresult function ####
def geturlresult(url):
    try:
        connection = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        return ""
    else:
        return connection.read().rstrip()



############################# main program ###################################
usage = \
"""
esmiles to xyz program

  Usage: arrows_esmiles2xyz -j esmiles xyzfile

  -j view with jmol
  -h prints this message

"""

print "esmiles2xyz Arrows version"
tt      = time.localtime()

abbreviation = "no abbreviation"
viewjmol = False
opts, args = getopt.getopt(sys.argv[1:], "hj")
for o, a in opts:
  if '-j' in o:
     viewjmol = True
  if o in ("-h","--help"):
    print usage
    exit()

if (len(args)<2): 
   print usage
   exit()

esmiles = args[0]
xyzfile = args[1]
arrows_url = 'https://arrows.pnnl.gov/api/esmiles2xyz/\"' + esmiles.replace("/","arrowslash").strip() + '\"'
print "esmiles     =",esmiles
print "xyzfile     =",xyzfile
print "arrows_url  =",arrows_url

try:
   rr = geturlresult(arrows_url)
   esmiles_dict = json.loads(rr)
except:
   try:
      rr = geturlresult(arrows_url)
      esmiles_dict = json.loads(rr)
   except:
      print " - API Failed"

#try:
#   rr = requests.get(arrows_url)
#   hh = rr.text
#   esmiles_dict = json.loads(hh)
#except:
#   try:
#      rr = requests.get(arrows_url)
#      hh = rr.text
#      esmiles_dict = json.loads(hh)
#   except:
#      print " - API Failed"

xyz_blob = esmiles_dict['xyz_blob']


print 
print "Fetched the following entry:"
if 'id' in esmiles_dict: print "id            = ",esmiles_dict['id']
print "synonyms = ",esmiles_dict['abbreviations']
print "mformula = ",esmiles_dict['mformula']
print "iupac    = ",esmiles_dict['iupac']
print "smiles   = ",esmiles_dict['smiles']
print "csmiles  = ",esmiles_dict['csmiles']
print "esmiles  = ",esmiles_dict['esmiles']
print "inchi    = ",esmiles_dict['inchi']
print "inchikey = ",esmiles_dict['inchikey']
print "cid      = ",esmiles_dict['cid']
print "cas      = ",esmiles_dict['cas']
print "kegg     = ",esmiles_dict['kegg']
print "bonding_string  = ",esmiles_dict['bonding_string']
print "covalent_string = ",esmiles_dict['covalent_string']
print "charge          = ",esmiles_dict['charge']
print "mult            = ",esmiles_dict['mult']
print "valence_charge  = ",esmiles_dict['valence_charge']
print "optimized       = ",esmiles_dict['optimized']
#print "ascii_art       = ",esmiles_dict['chemical_structure_ascii_art']



#with open(xyzfile,'r') as ff: 
#   xyzstring = ff.read()
#print xyzstring
print xyz_blob

if viewjmol:
   with open(xyzfile,'w') as ff:
      ff.write(xyz_blob)
   cmd6 = jmol + xyzfile
   os.system(cmd6)

