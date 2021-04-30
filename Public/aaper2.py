#!/usr/bin/python
from flask import Flask, jsonify, render_template
from flask import abort
import subprocess,urllib2

chemdb_fetch_esmiles5  = "/srv/arrows/bin/chemdb_fetch_esmiles5 "
chemdb_fetch_reactions = "/srv/arrows/bin/chemdb_fetch_reactions5 "
tnt_submit             = "/srv/arrows/bin/tnt_submit4 -f "
wrkdir                 = "/srv/arrows/Work"
templatedir            = "/srv/arrows/Public/templates"
staticdir              = "/srv/arrows/Public/static"

headerfigure = ['<a href="http://dl.dropboxusercontent.com/s/1fdkluujb97tr0b/banner2.gif"><img src="http://dl.dropboxusercontent.com/s/1fdkluujb97tr0b/banner2.gif" alt="Arrows Banner Movie"> </a>', '<a href="http://dl.dropboxusercontent.com/s/en5l9l7l31ggz6e/EMSL_banner.jpg"><img src="http://dl.dropboxusercontent.com/s/en5l9l7l31ggz6e/EMSL_banner.jpg" alt="EMSL Computing Banner" border=0 /></a>', '<a href="http://dl.dropboxusercontent.com/s/rcoee0m9urc4e3o/Surface-uprot.gif"><img src="http://dl.dropboxusercontent.com/s/rcoee0m9urc4e3o/Surface-uprot.gif" alt="Arrows Movie" width="200" height="200"> </a>', '<a href="https://dl.dropboxusercontent.com/s/chxhlvamd8ro356/ArrowsBeaker2.gif"><img src="http://dl.dropboxusercontent.com/s/chxhlvamd8ro356/ArrowsBeaker2.gif" alt="Arrows Movie"> </a>']

##### define the arrows logos #####
ArrowsHeader = '''
   <center> <p><b>EMSL Arrows: Evolultion of Chemical and Materials Simulations</b></p></center>
   <center> <p>Making molecular modeling accessible by combining NWChem, databases, web APIs, and email</p> </center>
   <center> %s </center>
''' % headerfigure[0]


#### geturlresult function ####
def geturlresult(url):
    try:
        connection = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        return ""
    else:
        return connection.read().rstrip()


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



app = Flask(__name__)

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

@app.route('/arrows/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/arrows/api/v1.0/id/<int:task_id>', methods=['GET'])
def get_arrowid(task_id):
    try:
       #task = [task for task in tasks if task['id'] == task_id]
       esmiles = "id=%d" % task_id
       cmd7 = chemdb_fetch_esmiles5 + '\"' + esmiles + '\"'
       data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT)
       if len(data) == 0: data=esmiles + " not found\n"
    except:
       data = '????'
    return data
    #return jsonify({'task': task[0]})

@app.route('/arrows/api/v1.0/esmiles/<esmiles0>', methods=['GET'])
def get_esmiles(esmiles0):
    try:
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       #print "esmiles=",esmiles0
       cmd7 = chemdb_fetch_esmiles5 + '\"' + esmiles0 + '\"'
       data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT)
       if len(data) == 0: data=esmiles0 + " not found\n"
    except:
       data = '????'

    return data

@app.route('/arrows/api/v1.0/molecule/<esmiles0>', methods=['GET'])
def get_molecule(esmiles0):
    try:
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       inpfile =  wrkdir + "/moleculetmp.txt"
       outfile =  wrkdir + "/moleculetmp.plain"
       with open(inpfile,'w') as ff:
          ff.write("molecule: " + esmiles0 + " :molecule\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile
       result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT)
       with open(outfile,'r') as ff:
          data = ff.read()
       if len(data) == 0: data=esmiles0 + " not found\n"
    except:
       data = '????'
        
    return data
    #return jsonify({'task': task[0]})

@app.route('/arrows/api/v1.0/reaction/<esmiles0>', methods=['GET'])
def get_reaction(esmiles0):
    try:
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       inpfile =  wrkdir + "/moleculetmp.txt"
       outfile =  wrkdir + "/moleculetmp.plain"
       htmlfile =  templatedir + "/moleculetmp2.html"
       with open(inpfile,'w') as ff:
          ff.write("reaction: " + esmiles0 + " :reaction\n")
       cmd7 = chemdb_fetch_reactions + inpfile + " " + outfile + " " + htmlfile
       result = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT)
       imagelist = result.split("imagelist:")[1].split(":imagelist")[0]
       images = [(imagelist.split()[i],imagelist.split()[i+1]) for i in range(0,len(imagelist.split()),2)]
       print "images=",images
       with open(htmlfile,'r') as ff:
          html = ff.read()
       delimages = []
       for a in images:
          a1 = "cid:"+a[1]
          a2 = " {{ url_for('static',filename='%s')}}" % a[0].split("/")[-1]
          delimages.append(staticdir + "/" + a[0].split("/")[-1]
          cmd8 = "mv " + a[0] + " " + staticdir
          result2 = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT)
          print "a1=",a1
          print "a2=",a2
          html = html.replace(a1,a2)
       with open(htmlfile,'w') as ff:
          ff.write(html)

       data = render_template('moleculetmp2.html')
       for image in delimages:

    except:
       data = '????'

    return data
    #return data


@app.route('/arrows/api/v1.0/input_deck/<esmiles0>', methods=['GET'])
def get_input_deck(esmiles0):
    try:
       esmiles0 = esmiles0.replace("\"",'')
       esmiles0 = esmiles0.replace("\'",'')
       esmiles0 = addspaces_reaction(esmiles0.strip())
       esmiles0 = parsetosmiles(esmiles0)
       cmd7 = tnt_submit + '\"' + esmiles0 + '\"'
       data = subprocess.check_output(cmd7,shell=True,stderr=subprocess.STDOUT)
       #print "- input_deck: esmiles=",esmiles0
       if len(data) == 0: data=esmiles0 + " not generated\n"
       html = "<html>\n" 
       html += ArrowsHeader
       html += "<pre style=\"font-size:0.6em;color:blue\">\n"
       html += data
       html += "</pre> </html>"
    except:
       html = "Input generation failed\n"
    return html


@app.route('/arrows/api/v1.0/calculation/', methods=['GET'])
def get_calculation():
   try:
      cmd8 = chemdb_fetch_esmiles5 + '-c'
      calcs = subprocess.check_output(cmd8,shell=True,stderr=subprocess.STDOUT)
   except:
      calcs = "calculations not found\n"
   return calcs


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
