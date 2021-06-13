#!/usr/local/bin/python2.7
import os,sys,getopt,math,copy
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




############################# main program ###################################
usage = \
"""
sdf2atype

  Usage: sdf2atyp -h sdf_filename

  -h help

"""

print

opts, args = getopt.getopt(sys.argv[1:], "h")
for o, a in opts:
  if o in ("-h","--help"):
    print usage
    exit()

if (len(args)<1):
   print usage
   exit()


filename = args[0]

with open(filename,'r') as ff:
   sdf = ff.read()


(nion,symbol,rion,amatrix) = xyzsdf2amatrix(sdf)

print "nion=",nion
print "symbol=",symbol
print "rion=",rion
print "amatrix=",amatrix

uff1 = uff_potential.uff_potential(nion,symbol,amatrix)


print "uff1=",uff1

print "bondstretch testing"
(E,grad) = uff1.bondstretch_egrad(nion,rion)
print "E=",E
print "grad=",grad
delta = 0.001

grad_num = [0.0]*3*nion
for i in range(3*nion):
   rionp = copy.deepcopy(rion)
   rionm = copy.deepcopy(rion)
   rionp[i] += delta
   rionm[i] -= delta
   (Ep,grad) = uff1.bondstretch_egrad(nion,rionp)
   (Em,grad) = uff1.bondstretch_egrad(nion,rionm)
   grad_num[i] = (Ep-Em)/(2.0*delta)
print "grad_num=",grad_num

print
print "anglebend testing"
(E,grad) = uff1.anglebend_egrad(nion,rion)
print "E=",E
print "grad=",grad
delta = 0.001
grad_num = [0.0]*3*nion
for i in range(3*nion):
   rionp = copy.deepcopy(rion)
   rionm = copy.deepcopy(rion)
   rionp[i] += delta
   rionm[i] -= delta
   (Ep,grad) = uff1.anglebend_egrad(nion,rionp)
   (Em,grad) = uff1.anglebend_egrad(nion,rionm)
   grad_num[i] = (Ep-Em)/(2.0*delta)
print "grad_num=",grad_num

print
print "torsion testing"
(E,grad) = uff1.torsion_egrad(nion,rion)
print "E=",E
print "grad=",grad
delta = 0.001
grad_num = [0.0]*3*nion
for i in range(3*nion):
   rionp = copy.deepcopy(rion)
   rionm = copy.deepcopy(rion)
   rionp[i] += delta
   rionm[i] -= delta
   (Ep,grad) = uff1.torsion_egrad(nion,rionp)
   (Em,grad) = uff1.torsion_egrad(nion,rionm)
   grad_num[i] = (Ep-Em)/(2.0*delta)
print "grad_num=",grad_num

print
print "inversion testing="
(E,grad) = uff1.inversion_egrad(nion,rion)
print "E=",E
print "grad=",grad
delta = 0.001
grad_num = [0.0]*3*nion
for i in range(3*nion):
   rionp = copy.deepcopy(rion)
   rionm = copy.deepcopy(rion)
   rionp[i] += delta
   rionm[i] -= delta
   (Ep,grad) = uff1.inversion_egrad(nion,rionp)
   (Em,grad) = uff1.inversion_egrad(nion,rionm)
   grad_num[i] = (Ep-Em)/(2.0*delta)
print "grad_num=",grad_num


eold = 9.0e9
grad = [0.0]*3*nion
alpha = 0.000001
it = 0
done = False
while (not done) and (it<55001):
   (E,grad) = uff1.egrad(nion,rion)
   if (E>eold): alpha *= 0.1

   err = 0.0
   for i in range(3*nion): err += grad[i]*grad[i]
   print "it,E=",it,E,err,alpha

   for i in range(3*nion):
     rion[i] -= alpha*grad[i]
   eold = E
   done = (err<1.0e-3)
   it +=1
   if ((it%10000)==0): alpha = 0.00001

print "Efinal=",E
print "rion=",rion
print "grad  =",grad
print "writing jjj.xyz"
with open("jjj.xyz",'w') as ff:
   ff.write("%d\n\n" % nion)
   for ii in range(nion):
      ff.write("%s %f %f %f\n" % (symbol[ii],rion[3*ii],rion[3*ii+1],rion[3*ii+2]))

print "writing jjj.mol"
with open("jjj.mol",'w') as ff:
   ff.write(uff1.print_mol(nion,symbol,amatrix,rion))

(E,grad) = uff1.bondstretch_egrad(nion,rion)
print "Ebondstretch=",E
(E,grad) = uff1.anglebend_egrad(nion,rion)
print "Eanglebend  =",E
(E,grad) = uff1.torsion_egrad(nion,rion)
print "Etorsion    =",E
(E,grad) = uff1.inversion_egrad(nion,rion)
print "Einversion  =",E
