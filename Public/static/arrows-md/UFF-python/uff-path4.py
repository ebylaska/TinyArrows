#!/usr/local/bin/python2.7
import os,sys,getopt,math,copy,random
import uff_potential





covalentstr = '''
H 32 0 0 0
He 46 0 0 0
Li 133 124 0 0
Be 102 90 85 0
B 85 78 73 0
C 75 67 60 68
N 71 60 54 0
O 63 57 53 0
F 64 59 53 0
Ne 67 96 0 0
Na 155 160 0 0
Mg 139 132 127 0
Al 126 113 111 0
Si 116 107 102 0
P 111 102 94 0
S 103 94 95 0
Cl 99 95 93 0
Ar 96 107 96 0
K 196 193 0 0
Ca 171 147 133 0
Sc 148 116 114 0
Ti 136 117 108 0
V 134 112 106 0
Cr 122 111 103 0
Mn 119 105 103 0
Fe 116 109 102 0
Co 111 103 96 0
Ni 110 101 101 0
Cu 112 115 120 0
Zn 118 120 0 0
Ga 124 116 121 0
Ge 121 111 114 0
As 121 114 106 0
Se 116 107 107 0
Br 114 109 110 0
Kr 117 121 108 0
Rb 210 202 0 0
Sr 185 157 139 0
Y 163 130 124 0
Zr 154 127 121 0
Nb 147 125 116 0
Mo 138 121 113 0
Tc 128 120 110 0
Ru 125 114 103 0
Rh 125 110 106 0
Pd 120 117 112 0
Ag 128 139 137 0
Cd 136 144 0 0
In 142 136 146 0
Sn 140 130 132 0
Sb 140 133 127 0
Te 136 128 121 0
I 133 129 125 0
Xe 131 135 122 0
Cs 232 196 0 0
Ba 196 161 149 0
La 180 139 139   0
Ce 163 137 131 0
Pr 176 138 128 0
Nd 174 137 0 0
Pm 173 135 0 0
Sm 172 134 0 0
Eu 168 134 0 0
Gd 169 135 132 0
Tb 168 135 0 0
Dy 167 133 0 0
Ho 166 133 0 0
Er 165 133 0 0
Tm 164 131 0 0
Yb 170 129 0 0
Lu 162 131 131   0
Hf 152 128 122   0
Ta 146 126 119   0
W 137 120 115    0
Re 131 119 110   0
Os 129 116 109   0
Ir 122 115 107   0
Pt 123 112 110   0
Au 124 121 123 0
Hg 133 142 0 0
Tl 144 142 150 0
Pb 144 135 137 0
Bi 151 141 135 0
Po 145 135 129 0
At 147 138 138 0
Rn 142 145 133 0
Fr 223 218 0 0
Ra 201 173 159 0
Ac 186 153 140 0
Th 175 143 136   0
Pa 169 138 129   0
U 170 134 118 0
Np 171 136 116 0
Pu 172 135 0  0
Am 166 135 0 0
Cm 166 136 0 0
Bk 168 139 0 0
Cf 168 140 0 0
Es 165 140 0 0
Fm 167 0 0 0
Md 173 139 0 0
No 176 0 0  0
Lr 161 141 0 0
Rf 157 140 131 0
Db 149 136 126 0
Sg 143 128 121 0
Bh 141 128 119 0
Hs 134 125 118 0
Mt 129 125 113 0
Ds 128 116 112 0
Rg 121 116 118   0
Cn 122 137 130 0
Uut 136 0 0 0
Fl 143 0 0 0
Uup 162  0 0 0
Lv 175 0 0 0
Uus 165 0 0 0
Uuo 157  0 0 0
'''
rcovalent = {}
for ln in covalentstr.strip().split('\n'):
   ss = ln.split()
   rcovalent[ss[0]] = (0.01*eval(ss[1]),0.01*eval(ss[2]),0.01*eval(ss[3]),0.01*eval(ss[4]))


###########################################
#                                         #
#              bond_order                 #
#                                         #
###########################################
def bond_order(rc1,rc2,r12):
   dd = 0.0001
   cov = (abs(r12-(rc1[0]+rc2[0]))/(rc1[0]+rc2[0]+dd),
          abs(r12-(rc1[1]+rc2[1]))/(rc1[1]+rc2[1]+dd),
          abs(r12-(rc1[2]+rc2[2]))/(rc1[2]+rc2[2]+dd),
          abs(r12-(rc1[3]+rc2[3]))/(rc1[3]+rc2[3]+dd))
   imin = 0
   dmin = cov[0]
   if (cov[1]<dmin):
      dmin = cov[1]
      imin = 1
   if (cov[2]<dmin):
      dmin = cov[2]
      imin = 2
   if (cov[3]<dmin):
      dmin = cov[3]
      imin = 3
   b = 0
   if (cov[imin]<0.10):
      b = 1+imin
      if (imin==3):
         b = 1.5
   return b



##############################################
#                                            #
#            xyzsdf2amatrix                  #
#                                            #
##############################################

def xyzsdf2amatrix(sdf):

   ### parse mol, sdf file ###
   if "V2000" in sdf:
      nion  = eval(sdf.split("V2000")[0].split("\n")[-1].split()[0])
      nbond = eval(sdf.split("V2000")[0].split("\n")[-1].split()[1])
      print "nions =", nion
      print "nbonds=", nbond
      geom = "\n".join(sdf.split("V2000")[1].split("\n")[1:nion+1])
      print "geom="
      print  geom
      bonding = "\n".join(sdf.split("V2000")[1].split("\n")[nion+1:nion+1+nbond])
      print "bonding="
      print bonding
      amatrix = [0]*nion*nion
      symbol = []
      rxyz   = []
      ### this will change in javascript - currently doesn't handle +4 charge
      i = 0
      for aa in geom.split("\n"):
         ss = aa.split()
         qq = eval(ss[5])
         if (abs(qq)>1.0e-6):
            qq = 4-qq
            amatrix[i+i*nion] = qq
         rxyz.append(eval(ss[0]))
         rxyz.append(eval(ss[1]))
         rxyz.append(eval(ss[2]))
         symbol.append(ss[3])
         i += 1

   ### parse xyz file ###
   else:
      nbond = 0
      nion = eval(sdf.split("\n")[0].strip())
      print "nions =", nion
      print "assuming xyz data"
      amatrix = [0]*nion*nion
      symbol = []
      rxyz   = []
      for aa in sdf.strip().split("\n")[2:]:
         ss = aa.split()
         symbol.append(ss[0])
         rxyz.append(eval(ss[1]))
         rxyz.append(eval(ss[2]))
         rxyz.append(eval(ss[3]))
      
   ### build amatrix from geometry ###
   if (nbond==0):
      for i in range(nion):
         for j in range(nion):
            symi = symbol[i]
            symj = symbol[j]
            rci   = rcovalent[symbol[i]]
            rcj   = rcovalent[symbol[j]]
            dx = rxyz[3*i]   - rxyz[3*j]
            dy = rxyz[3*i+1] - rxyz[3*j+1]
            dz = rxyz[3*i+2] - rxyz[3*j+2]
            r = math.sqrt(dx*dx + dy*dy + dz*dz)
            if i!=j:
               b = bond_order(rci,rcj,r)
               if (b<1.0) and (symi==symj) and (r<(2.5*rci[0])): b = 1
               amatrix[i+j*nion] = b

   ### build amatrix from bonding data ###
   else:
      for bb in bonding.split("\n"):
         ss = bb.split()
         i = eval(ss[0])-1
         j = eval(ss[1])-1
         v = eval(ss[2])
         amatrix[i+j*nion] = v
         amatrix[j+i*nion] = v

   return (nion,symbol,rxyz,amatrix)


###########################################
#                                         #
#          simple_optimization            #
#                                         #
###########################################
def simple_optimization(uff1,uff2,lmbda12,nion,rion0):
   rion = copy.deepcopy(rion0)
   grad = [0.0]*3*nion
   ### do a crude optimization ###
   eold = 9.0e9
   alpha = 0.0001
   acount = 0
   it = 0
   done = False
   while (not done) and (it<55001):
      (E1,grad1) = uff1.egrad(nion,rion)
      (E2,grad2) = uff2.egrad(nion,rion)
      E = (1.0-lmbda12)*E1 + lmbda12*E2
      for i in range(3*nion): grad[i] = (1.0 - lmbda12)*grad1[i] + lmbda12*grad2[i]

      if (E>eold):
         alpha *= 0.1
         acount = 0
      else:
         acount += 1
         if (acount>100):
            alpha *= 2
            acount = 0

      err = 0.0
      for i in range(3*nion): err += grad[i]*grad[i]
      print "optimize,lmbda,it,E=",lmbda,lmbda12,it,E,err,alpha,l

      for i in range(3*nion):
        rion[i] -= alpha*grad[i]
      eold = E
      done = (err<1.0e-3)
      it +=1
      if ((it%10000)==0): alpha = 0.0001

   return (E,rion,grad)

###########################################
#                                         #
#          simple_optimization1           #
#                                         #
###########################################
def simple_optimization1(uff1,nion,rion0):
   rion = copy.deepcopy(rion0)
   grad = [0.0]*3*nion
   ### do a crude optimization ###
   eold = 9.0e9
   alpha = 0.0001
   acount = 0
   it = 0
   done = False
   while (not done) and (it<75001):
      (E,grad) = uff1.egrad(nion,rion)

      if (E>eold):
         alpha *= 0.1
         acount = 0
      else:
         acount += 1
         if (acount>100):
            alpha *= 2
            acount = 0

      err = 0.0
      for i in range(3*nion): err += grad[i]*grad[i]
      print "optimize0,lmbda,it,E=",lmbda,it,E,err,alpha

      for i in range(3*nion):
        rion[i] -= alpha*grad[i]
      eold = E
      done = (err<1.0e-3)
      it +=1
      if ((it%10000)==0): alpha = 0.0001

   return (E,rion,grad)


############################# main program ###################################
usage = \
"""
uff-path4

  Usage: uff-path4 -h xyzsdf_filename bondchange_string nbisections

     where bondchange_string = "( ([i1,j1,b1],[i2,j2,b2],...), ([k1,l1,c1],[k2,l2,c2],...) )"
     e.g. 
      uff-path4 -h xyzsdf_filename "((),([1,4,1], [6,12,1]))" npath

  -h help

"""

print

opts, args = getopt.getopt(sys.argv[1:], "h")
for o, a in opts:
  if o in ("-h","--help"):
    print usage
    exit()

if (len(args)<3):
   print usage
   exit()


filename  = args[0]
bondchanges = eval(args[1])
nbisection  = eval(args[2])

### load xyz or mol file ###
with open(filename,'r') as ff:  sdf  = ff.read()
(nion,symbol,rion,amatrix)     = xyzsdf2amatrix(sdf)

### generate uff potentials ###
nstates = len(bondchanges)
uff = []
for n in range(nstates):
   amatrix1 = copy.deepcopy(amatrix)
   for ab in bondchanges[n]: ## add bonds ##
      i = ab[0] - 1
      j = ab[1] - 1
      b = ab[2]
      amatrix1[i+j*nion] = b
      amatrix1[j+i*nion] = b
   uff.append(uff_potential.uff_potential(nion,symbol,amatrix1))

### generate an initial path ###
pathlmbda = []
pathxyz = []
pathe   = []
lmbda = 0.0
dnstates = 1.0/float(nstates-1)
for n in range(nstates):
   lmbda = n*dnstates
   (E,rion,grad) = simple_optimization1(uff[n],nion,rion)
   pathlmbda.append(lmbda)
   pathxyz.append(rion)
   pathe.append(E)

   if (n<(nstates-1)):
      lmbda12 = 0.5*dnstates
      lmbda += lmbda12
      l = pmax = n
      (E,rion,grad) = simple_optimization(uff[n],uff[n+1],lmbda12,nion,rion)
      pathlmbda.append(lmbda)
      pathxyz.append(rion)
      pathe.append(E)


for b in range(nbisection):
   demax = 0.0
   pmax  = 0
   npath = len(pathe)
   for p in range(npath-1):
      de = abs(pathe[p+1]-pathe[p])
      if (de>demax):
         demax = de
         pmax  = p
   
   lmbda = (pathlmbda[pmax] + pathlmbda[pmax+1])/2.0
   l = int(lmbda/dnstates)
   print "l,lmbda,dnstates=",l,lmbda,dnstates,len(uff)
   uff1 = uff[l]
   uff2 = uff[l+1]
   lmbda12 = lmbda - l*dnstates
   print "pmax,lmbda,lmbda12,l=",pmax,lmbda,lmbda12,l,demax,abs(pathe[1] - pathe[0])
   print "pathe=",pathe

   (E,rion,grad)    = simple_optimization(uff1,uff2,lmbda12,nion,pathxyz[pmax])
   (E1,rion1,grad1) = simple_optimization(uff1,uff2,lmbda12,nion,pathxyz[pmax+1])
   if (E1<E):
      E = E1
      rion = rion1
      grad = grad1

   print "Efinal=",E
   print "rion=",rion
   print "grad  =",grad
   pathlmbda.insert(pmax+1,lmbda)
   pathxyz.insert(pmax+1,rion)
   pathe.insert(pmax+1,E)


pathstr = ''
npath = len(pathxyz)
for p in range(npath):
   pathstr += "%d\n\n" % nion
   for ii in range(nion):
      pathstr += "%s %f %f %f\n" % (symbol[ii],pathxyz[p][3*ii],pathxyz[p][3*ii+1],pathxyz[p][3*ii+2])


print "writing final_path4.xyz"
with open("final_path4.xyz",'w') as ff: ff.write(pathstr)

print "writing final_path4.dat"
npath = len(pathe)
with open("final_path4.dat",'w') as ff:
   for p in range(npath):
      ff.write("%f %f\n" % (pathlmbda[p],pathe[p]))

