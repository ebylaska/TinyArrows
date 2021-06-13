


def xyzsdf2amatrix(sdf):

   ### parse mol, sdf file ###
   if "V2000" in sdf:
      nion  = eval(sdf.split("V2000")[0].split("\n")[-1].split()[0])
      nbond = eval(sdf.split("V2000")[0].split("\n")[-1].split()[1])
      #print "nions =", nion
      #print "nbonds=", nbond
      geom = "\n".join(sdf.split("V2000")[1].split("\n")[1:nion+1])
      #print "geom="
      #print  geom
      bonding = "\n".join(sdf.split("V2000")[1].split("\n")[nion+1:nion+1+nbond])
      #print "bonding="
      #print bonding
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
      #print "nions =", nion
      #print "assuming xyz data"
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


