        
console.log("Loading arrows-static/arrows-md/bylaska.md.js");


/********************************* Bylaska MD Potential *******************************************/
/**********************************************
 *                                            *
 *                 Bylaska_MD                 *
 *                                            * 
 **********************************************/

/* A simple MD class.  Currently only 12-6 Lennard-Jones
   is implemented.

   units - sigma:Angstroms and epsilon:kcal/mol 
*/

class Bylaska_MD {
   constructor(potential_input,nion,symbols) {
      this.potential_input = potential_input;

      this.default_sigma   = 3.3; 
      this.default_epsilon = 0.12;
      // LJ parameters for FCC metals - Hendrik Heinz,,R.A. Vaia, B.L. Farmer, and R.R. Naik; J. Phys. Chem. C2008,112,17281–17290
      // units are kcal/mol and Angstroms
      if (potential_input.includes("lj-potential-fcc-metals")) {
         this.el_sigma   = {"Ag" : 2.955, "Al" : 2.925, "Au" : 2.951, "Cu" : 2.616, "Ni" : 2.552, "Pb" : 3.565, "Pd" : 2.819, "Pt" : 2.845}; 
         this.el_epsilon = {"Ag" : 4.56,  "Al" : 4.02,  "Au" : 5.29,  "Cu" : 4.72,  "Ni" : 5.65,  "Pb" : 2.93,  "Pd" : 6.15,  "Pt" : 7.80 };
      }
      this.rcell = [0.0,0.0,0.0];
      this.nshl3d = this.rcell.length;

      this.nion = nion
      this.symbols = symbols;
      this.sigma   = new Array(this.nion); 
      this.epsilon = new Array(this.nion); 
      for (let ii=0; ii<(this.nion); ++ii) {
         if (symbols[ii] in this.el_sigma) {
            this.sigma[ii]             = this.el_sigma[symbols[ii]];
         } else {
            this.sigma[ii]             = this.default_sigma;
            this.el_sigma[symbols[ii]] = this.default_sigma;
         }
         if (symbols[ii] in this.el_epsilon) {
            this.epsilon[ii]             = this.el_epsilon[symbols[ii]];
         } else {
            this.epsilon[ii]             = this.default_epsilon;
            this.el_epsilon[symbols[ii]] = this.default_epsilon;
         }
      }
   }

   /*****************************
    *       mdlat               *
    *****************************/
   mdlat_setter(a1,a2,a3) {
      let  b1 = [a2[1]*a3[2]-a2[2]*a3[1], a2[2]*a3[0]-a2[0]*a3[2], a2[0]*a3[1]-a2[1]*a3[0]];
      let  b2 = [a3[1]*a1[2]-a3[2]*a1[1], a3[2]*a1[0]-a3[0]*a1[2], a3[0]*a1[1]-a3[1]*a1[0]];
      let  b3 = [a1[1]*a2[2]-a1[2]*a2[1], a1[2]*a2[0]-a1[0]*a2[2], a1[0]*a2[1]-a1[1]*a2[0]];
      let vol = a1[0]*b1[0] + a1[1]*b1[1] + a1[2]*b1[2];
      b1[0] /= vol; b1[1] /= vol; b1[2] /= vol;
      b2[0] /= vol; b2[1] /= vol; b2[2] /= vol;
      b3[0] /= vol; b3[1] /= vol; b3[2] /= vol;
      this.mdlat = [a1,a2,a3,b1,b2,b3];

      this.nshl3d = 1;
      this.rcell  = [0.0,0.0,0.0];
      for (let n3=-3; n3<4; ++n3) {
         for (let n2=-3; n2<4; ++n2) {
            for (let n1=-3; n1<4; ++n1) {
               if (!((n3==0) && (n2==0) && (n1==0))) {
                  let xx = (n1*a1[0] + n2*a2[0] + n3*a3[0]);
                  let yy = (n1*a1[1] + n2*a2[1] + n3*a3[1]);
                  let zz = (n1*a1[2] + n2*a2[2] + n3*a3[2]);
                  let r = Math.sqrt(xx*xx + yy*yy + zz*zz);
                  if (r<25.0) {
                     this.rcell.push(xx);
                     this.rcell.push(yy);
                     this.rcell.push(zz);
                     this.nshl3d += 1;
                  }
               }
            }
         }
      }
   }

   mdlat_min_diff(dx,dy,dz) {
      if (this.mdlat.length==6) {
         let c0 = this.mdlat[3][0]*dx + this.mdlat[3][1]*dy + this.mdlat[3][2]*dz;
         let c1 = this.mdlat[4][0]*dx + this.mdlat[4][1]*dy + this.mdlat[4][2]*dz;
         let c2 = this.mdlat[5][0]*dx + this.mdlat[5][1]*dy + this.mdlat[5][2]*dz;
         c0 = c0 - Math.round(c0);
         c1 = c1 - Math.round(c1);
         c2 = c2 - Math.round(c2);
         return [c0*this.mdlat[0][0] + c1*this.mdlat[1][0] + c2*this.mdlat[2][0],
                 c0*this.mdlat[0][1] + c1*this.mdlat[1][1] + c2*this.mdlat[2][1],
                 c0*this.mdlat[0][2] + c1*this.mdlat[1][2] + c2*this.mdlat[2][2]];
      } else {
         return [dx,dy,dz];
      }
   }



   all_e(nion,rion) {

      // pairwise potentials 
      let energy = 0.0;
      for (let ii=0; ii<(nion-1); ++ii) {
         for (let jj=ii+1; jj<nion; ++jj) {
            let sij = 0.5*(this.sigma[ii]+this.sigma[jj]);
            let eij = Math.sqrt(this.epsilon[ii]*this.epsilon[jj]);

            let [dx,dy,dz] = this.mdlat_min_diff(rion[3*ii]-rion[3*jj],rion[3*ii+1]-rion[3*jj+1],rion[3*ii+2]-rion[3*jj+2]);
            for (let l=0; l<this.nshl3d; ++l) {
               let x = dx + this.rcell[3*l];
               let y = dy + this.rcell[3*l+1];
               let z = dz + this.rcell[3*l+2];

               let r2 = x*x + y*y + z*z;
               let u2 = (sij*sij)/r2;
               let u6  = u2*u2*u2;
               let u12 = u6*u6;
           
               energy += 4.0*eij*(u12 - u6);
            }
         }
      }
      return energy;
   }

   all_egrad(nion,rion) {
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0};
     
      let E = 0.0;
      for (let ii=0; ii<(nion-1); ++ii) {
         for (let jj=ii+1; jj<nion; ++jj) {
            let sij = 0.5*(this.sigma[ii]+this.sigma[jj]);
            let eij = Math.sqrt(this.epsilon[ii]*this.epsilon[jj]);

            let [dx,dy,dz] = this.mdlat_min_diff(rion[3*ii]-rion[3*jj],rion[3*ii+1]-rion[3*jj+1],rion[3*ii+2]-rion[3*jj+2]);
            for (let l=0; l<this.nshl3d; ++l) {
               let x = dx + this.rcell[3*l];
               let y = dy + this.rcell[3*l+1];
               let z = dz + this.rcell[3*l+2];

               let r2 = x*x + y*y + z*z;
               let r  = Math.sqrt(r2);
               let u2 = (sij*sij)/r2;
               let u6  = u2*u2*u2;
               let u12 = u6*u6;

               E += 4.0*eij*(u12 - u6);
               let dVdr = -4.0*eij/r*(12.0*u12 - 6.0*u6); 

               let fxii = (x/r)*dVdr;
               let fyii = (y/r)*dVdr;
               let fzii = (z/r)*dVdr;
               grad[3*ii]   += fxii;
               grad[3*ii+1] += fyii;
               grad[3*ii+2] += fzii;
               grad[3*jj]   -= fxii;
               grad[3*jj+1] -= fyii;
               grad[3*jj+2] -= fzii;
            
            }
         }
      }
      return [E,grad];
   }

   print_params() {
      const eoln = '\n';
      let astr = eoln;
      let katom_type = Array.from(new Set(this.symbols));
      astr += sprintf("Bylaska MD LJ Potential Parameters\n");
      astr += sprintf("%5s %8s %8s\n","atom","sigma", "epsilon");
      for (const symb of katom_type) {
         astr += sprintf("%5s %8.3f %8.3f\n",symb,this.el_sigma[symb],this.el_epsilon[symb]);
      }
      return astr;
   }

   print_mol(nion,symbol,amatrix,rion) {
      let nbonds = 0.0;
      for (let j=0; j<(nion-1); ++j) {
         for (let i=j+1; i<nion; ++i) {
            const aij = amatrix[i+j*nion];
            if (aij>0) { nbonds += 1; }
         }
      }
      const eoln = '\n';
      let astr = eoln;
      astr += ' EMSLArrows0000000001A' + eoln + eoln;
      astr += sprintf("%3d %2d  0  0  0  0  0  0  0  0999 V2000",nion,nbonds) + eoln;
      for (let i=0; i<nion; ++i) {
         astr += sprintf(" %9.4f %9.4f %9.4f %s",rion[3*i],rion[3*i+1],rion[3*i+2],symbol[i]);
         astr += "  0  0  0  0  0  0  0  0  0  0  0  0" + eoln;
      }

      for (let j=0; j<(nion-1); ++j) {
         for (let i=j+1; i<nion; ++i) {
            const aij = amatrix[i+j*nion];
            if (aij>0) {
               astr += sprintf("%3d %2d %2d",i+1,j+1,aij);
               astr += "  0  0  0  0" + eoln;
            }
         }
      }

      astr += 'M  END' + eoln;
      astr += '$$$$' + eoln;
      return astr;
   }

   print_xyz(nion,symbol,amatrix,rion) {
      const eoln = '\n';
      let astr = sprintf("%d\n\n",nion);
      for (let i=0; i<nion; ++i) {
         astr += sprintf("%s  %12.6f %12.6f %12.6f\n",symbol[i],rion[3*i],rion[3*i+1],rion[3*i+2]);
      }
      return astr;
   }
}
/********************************* Bylaska MD Potential *******************************************/



/*************************************** UFF Potential ********************************************/
/**********************************************
 *                                            *
 *                 UFF_Potential              *
 *                                            * 
 **********************************************/

/* A simple UFF MD Potential class.

   Reference: A.K.Rappe et al.,  J. Am. Chem. Soc. 1992, 114, 10024-10035

   units - Angstroms, Degrees, kcal/mol, Charge (atomic)
*/

var eric_periodic_table_charge = { 'H'  : 1, 'He' : 2, 'Li' : 3, 'Be' : 4, 'B'  : 5, 'C'  : 6, 'N'  : 7, 'O'  : 8, 'F'  : 9, 'Ne' : 10, 'Na' : 11, 'Mg' : 12, 'Al' : 13, 'Si' : 14, 'P'  : 15, 'S'  : 16, 'Cl' : 17, 'Ar' : 18, 'K'  : 19, 'Ca' : 20, 'Sc' : 21, 'Ti' : 22, 'V'  : 23, 'Cr' : 24, 'Mn' : 25, 'Fe' : 26, 'Co' : 27, 'Ni' : 28, 'Cu' : 29, 'Zn' : 30, 'Ga' : 31, 'Ge' : 32, 'As' : 33, 'Se' : 34, 'Br' : 35, 'Kr' : 36, 'Rb' : 37, 'Sr' : 38, 'Y'  : 39, 'Zr' : 40, 'Nb' : 41, 'Mo' : 42, 'Tc' : 43, 'Ru' : 44, 'Rh' : 45, 'Pd' : 46, 'Ag' : 47, 'Cd' : 48, 'In' : 49, 'Sn' : 50, 'Sb' : 51, 'Te' : 52, 'I'  : 53, 'Xe' : 54, 'Cs' : 55, 'Ba' : 56, 'La' : 57, 'Ce' : 58, 'Pr' : 59, 'Nd' : 60, 'Pm' : 61, 'Sm' : 62, 'Eu' : 63, 'Gd' : 64, 'Tb' : 65, 'Dy' : 66, 'Ho' : 67, 'Er' : 68, 'Tm' : 69, 'Yb' : 70, 'Lu' : 71, 'Hf' : 72, 'Ta' : 73, 'W'  : 74, 'Re' : 75, 'Os' : 76, 'Ir' : 77, 'Pt' : 78, 'Au' : 79, 'Hg' : 80, 'Tl' : 81, 'Pb' : 82, 'Bi' : 83, 'Po' : 84, 'At' : 85, 'Rn' : 86, 'Fr' : 87, 'Ra' : 88, 'Ac' : 89, 'Th' : 90, 'Pa' : 91, 'U'  : 92, 'Np' : 93, 'Pu' : 94, 'Am' : 95, 'Cm' : 96, 'Bk' : 97, 'Cf' : 98, 'Es' : 99, 'Fm' : 100, 'Md' : 101, 'No' : 102, 'Lr' : 103, 'Rf' : 104, 'Ha' : 105, 'Sg' : 106, 'Bh' : 107, 'Hs' : 108, 'Mt' : 109 };


var table_smartuff = `
atom [#1]     H_          Generic hydrogen
atom [#1D2]   H_b         Bridging hydrogen
atom [#2]     He4+4       Helium
atom [#3]     Li          Lithium
atom [#4]     Be3+2       Generic Be
atom [#5]     B_2         Trigonal planar boron
atom [#5D4]   B_3         Tetrahedral boron
atom [#6]     C_3         Generic sp3 C
atom [C^2]    C_2         sp2 non-aromatic C=
atom [C+1]    C_2+        trivalent C (cation)  // bh added Jmol 12.0.RC9
atom [C-1]    C_3         trivalent C (anion)  // bh added Jmol 12.0.RC9
atom [CA1]    C_2         allylic C (anion or cation) // bh added Jmol 12.0.RC9
atom [C^1]    C_1         sp hybridized C
atom [c]      C_R         aromatic C
atom [#7]     N_3         Generic sp3 N
atom [NA1]    N_2         allylic N or amide  // bh added Jmol 12.0.RC9
atom [N^2]    N_2         sp2 non-aromatic N  // bh was [ND2], but this improperly treats N-oxides
atom [N^1]    N_1         sp hybridized N     // bh was [ND1], but this is more specifically sp
atom [n]      N_R         aromatic N
atom [#8]     O_3         generic, sp3 hybridized O
atom [O^2]    O_2         sp2 hybridized O  
atom [O^1]    O_1         sp hybridized O
atom [o]      O_R         aromatic O
atom [#9]     F_          generic F
atom [#10]    Ne4+4       
atom [#11]    Na          
atom [#12]    Mg3+2
atom [#13]    Al3
atom [#14]    Si3
atom [#15+5]  P_3+5       formal charge +5
#atom [#15]   P_3+q       Organometallic phosphine ligands
atom [#15]    P_3+3       generic phosphorus
atom [#16]    S_3+2       generic S
atom [#16+4]  S_3+4       S+4
atom [#16+6]  S_3+6       S+6
atom [S^2]    S_2         non-aromatic sp2 S
atom [s]      S_R         aromatic S
atom [#17]    Cl
atom [#18]    Ar4+4
atom [#19]    K_
atom [#20]    Ca6+2
atom [#21]    Sc3+3
atom [#22]    Ti6+4       generic Ti (6-valent)
atom [#22D3]  Ti3+4
atom [#23]    V_3+5
atom [#24]    Cr6+3
atom [#25]    Mn6+2
atom [#26]    Fe6+2       generic Fe (6-valent)
atom [#26D3]  Fe3+2
atom [#27]    Co6+3
atom [#28]    Ni4+2
atom [#29]    Cu3+1
atom [#30]    Zn3+2
atom [#31]    Ga3+3
atom [#32]    Ge3
atom [#33]    As3+3
atom [#34]    Se3+2
atom [#35]    Br
atom [#36]    Kr4+4
atom [#37]    Rb
atom [#38]    Sr6+2
atom [#39]    Y_3+3
atom [#40]    Zr3+4
atom [#41]    Nb3+5
atom [#42]    Mo6+6       generic Mo (6-valent)
atom [#42D3]  Mo3+6       trivalent Mo
atom [#43]    Tc6+5
atom [#44]    Ru6+2
atom [#45]    Rh6+3
atom [#46]    Pd4+2
atom [#47]    Ag1+1
atom [#48]    Cd3+2
atom [#49]    In3+3
atom [#50]    Sn3
atom [#51]    Sb3+3
atom [#52]    Te3+2
atom [#53]    I_
atom [#54]    Xe4+4
atom [#55]     Cs
atom [#56]     Ba6+2
atom [#57]     La3+3
atom [#58]     Ce6+3
atom [#59]     Pr6+3
atom [#60]     Nd6+3
atom [#61]     Pm6+3
atom [#62]     Sm6+3
atom [#63]     Eu6+3
atom [#64]     Gd6+3
atom [#65]     Tb6+3
atom [#66]     Dy6+3
atom [#67]     Ho6+3
atom [#68]     Er6+3
atom [#69]     Tm6+3
atom [#70]     Yb6+3
atom [#71]     Lu6+3
atom [#72]     Hf3+4
atom [#73]     Ta3+5
atom [#74]     W_6+6       generic W (6-valent)
atom [#74D3+4] W_3+4
atom [#74D3+6] W_3+6
atom [#75]     Re6+5       generic Re (6-valent)
atom [#75D3]   Re3+7       trivalent Re
atom [#76]     Os6+6
atom [#77]     Ir6+3
atom [#78]     Pt4+2
atom [#79]     Au4+3
atom [#80]     Hg1+2
atom [#81]     Tl3+3
atom [#82]     Pb3
atom [#83]     Bi3+3
atom [#84]     Po3+2
atom [#85]     At
atom [#86]     Rn4+4
atom [#87]     Fr
atom [#88]     Ra6+2
atom [#89]     Ac6+3
atom [#90]     Th6+4
atom [#91]     Pa6+4
atom [#92]     U_6+4
atom [#93]     Np6+4
atom [#94]     Pu6+4
atom [#95]     Am6+4
atom [#96]     Cm6+3
atom [#97]     Bk6+3
atom [#98]     Cf6+3
atom [#99]     Es6+3
atom [#100]    Fm6+3
atom [#101]    Md6+3
atom [#102]    No6+3
atom [#103]    Lw6+3 `;
var eric_smartuff = {};
var tmpj = table_smartuff.trim().split('\n');
for (let i=0; i<tmpj.length; ++i) {
   let ss = tmpj[i].split(/\s+/);
   eric_smartuff[ss[1]] = ss[2];
}


//
// param Atom	r1	theta0	x1	D1	zeta	Z1	Vi	Uj	Xi	Hard	Radius
var table_uffparam = `
param H_	0.354	180	2.886	0.044	12	0.712	0	0	4.528	6.9452	0.371
param H_b	0.46	83.5	2.886	0.044	12	0.712	0	0	4.528	6.9452	0.371
param He4+4	0.849	90	2.362	0.056	15.24	0.098	0	0	9.66	14.92	1.3
param Li	1.336	180	2.451	0.025	12	1.026	0	2	3.006	2.386	1.557
param Be3+2	1.074	109.47	2.745	0.085	12	1.565	0	2	4.877	4.443	1.24
param B_3	0.838	109.47	4.083	0.18	12.052	1.755	0	2	5.11	4.75	0.822
param B_2	0.828	120	4.083	0.18	12.052	1.755	0	2	5.11	4.75	0.822
param C_3	0.757	109.47	3.851	0.105	12.73	1.912	2.119	2	5.343	5.063	0.759
param C_R	0.729	120	3.851	0.105	12.73	1.912	0	2	5.343	5.063	0.759
param C_2	0.732	120	3.851	0.105	12.73	1.912	0	2	5.343	5.063	0.759
param C_2+	0.732	120	6.851	0.105	12.73	1.912	0	2	5.343	5.063	0.759
param C_1	0.706	180	3.851	0.105	12.73	1.912	0	2	5.343	5.063	0.759
param N_3	0.7	106.7	3.66	0.069	13.407	2.544	0.45	2	6.899	5.88	0.715
param N_R	0.699	120	3.66	0.069	13.407	2.544	0	2	6.899	5.88	0.715
param N_2	0.685	111.2	3.66	0.069	13.407	2.544	0	2	6.899	5.88	0.715
param N_1	0.656	180	3.66	0.069	13.407	2.544	0	2	6.899	5.88	0.715
param O_3	0.658	104.51	3.5	0.06	14.085	2.3	0.018	2	8.741	6.682	0.669
param O_3_z	0.528	146	3.5	0.06	14.085	2.3	0.018	2	8.741	6.682	0.669
param O_R	0.68	110	3.5	0.06	14.085	2.3	0	2	8.741	6.682	0.669
param O_2	0.634	120	3.5	0.06	14.085	2.3	0	2	8.741	6.682	0.669
param O_1	0.639	180	3.5	0.06	14.085	2.3	0	2	8.741	6.682	0.669
param F_	0.668	180	3.364	0.05	14.762	1.735	0	2	10.874	7.474	0.706
param Ne4+4	0.92	90	3.243	0.042	15.44	0.194	0	2	11.04	10.55	1.768
param Na	1.539	180	2.983	0.03	12	1.081	0	1.25	2.843	2.296	2.085
param Mg3+2	1.421	109.47	3.021	0.111	12	1.787	0	1.25	3.951	3.693	1.5
param Al3	1.244	109.47	4.499	0.505	11.278	1.792	0	1.25	4.06	3.59	1.201
param Si3	1.117	109.47	4.295	0.402	12.175	2.323	1.225	1.25	4.168	3.487	1.176
param P_3+3	1.101	93.8	4.147	0.305	13.072	2.863	2.4	1.25	5.463	4	1.102
param P_3+5	1.056	109.47	4.147	0.305	13.072	2.863	2.4	1.25	5.463	4	1.102
param P_3+q	1.056	109.47	4.147	0.305	13.072	2.863	2.4	1.25	5.463	4	1.102
param S_3+2	1.064	92.1	4.035	0.274	13.969	2.703	0.484	1.25	6.928	4.486	1.047
param S_3+4	1.049	103.2	4.035	0.274	13.969	2.703	0.484	1.25	6.928	4.486	1.047
param S_3+6	1.027	109.47	4.035	0.274	13.969	2.703	0.484	1.25	6.928	4.486	1.047
param S_R	1.077	92.2	4.035	0.274	13.969	2.703	0	1.25	6.928	4.486	1.047
param S_2	0.854	120	4.035	0.274	13.969	2.703	0	1.25	6.928	4.486	1.047
param Cl	1.044	180	3.947	0.227	14.866	2.348	0	1.25	8.564	4.946	0.994
param Ar4+4	1.032	90	3.868	0.185	15.763	0.3	0	1.25	9.465	6.355	2.108
param K_	1.953	180	3.812	0.035	12	1.165	0	0.7	2.421	1.92	2.586
param Ca6+2	1.761	90	3.399	0.238	12	2.141	0	0.7	3.231	2.88	2
param Sc3+3	1.513	109.47	3.295	0.019	12	2.592	0	0.7	3.395	3.08	1.75
param Ti3+4	1.412	109.47	3.175	0.017	12	2.659	0	0.7	3.47	3.38	1.607
param Ti6+4	1.412	90	3.175	0.017	12	2.659	0	0.7	3.47	3.38	1.607
param V_3+5	1.402	109.47	3.144	0.016	12	2.679	0	0.7	3.65	3.41	1.47
param Cr6+3	1.345	90	3.023	0.015	12	2.463	0	0.7	3.415	3.865	1.402
param Mn6+2	1.382	90	2.961	0.013	12	2.43	0	0.7	3.325	4.105	1.533
param Fe3+2	1.27	109.47	2.912	0.013	12	2.43	0	0.7	3.76	4.14	1.393
param Fe6+2	1.335	90	2.912	0.013	12	2.43	0	0.7	3.76	4.14	1.393
param Co6+3	1.241	90	2.872	0.014	12	2.43	0	0.7	4.105	4.175	1.406
param Ni4+2	1.164	90	2.834	0.015	12	2.43	0	0.7	4.465	4.205	1.398
param Cu3+1	1.302	109.47	3.495	0.005	12	1.756	0	0.7	4.2	4.22	1.434
param Zn3+2	1.193	109.47	2.763	0.124	12	1.308	0	0.7	5.106	4.285	1.4
param Ga3+3	1.26	109.47	4.383	0.415	11	1.821	0	0.7	3.641	3.16	1.211
param Ge3	1.197	109.47	4.28	0.379	12	2.789	0.701	0.7	4.051	3.438	1.189
param As3+3	1.211	92.1	4.23	0.309	13	2.864	1.5	0.7	5.188	3.809	1.204
param Se3+2	1.19	90.6	4.205	0.291	14	2.764	0.335	0.7	6.428	4.131	1.224
param Br	1.192	180	4.189	0.251	15	2.519	0	0.7	7.79	4.425	1.141
param Kr4+4	1.147	90	4.141	0.22	16	0.452	0	0.7	8.505	5.715	2.27
param Rb	2.26	180	4.114	0.04	12	1.592	0	0.2	2.331	1.846	2.77
param Sr6+2	2.052	90	3.641	0.235	12	2.449	0	0.2	3.024	2.44	2.415
param Y_3+3	1.698	109.47	3.345	0.072	12	3.257	0	0.2	3.83	2.81	1.998
param Zr3+4	1.564	109.47	3.124	0.069	12	3.667	0	0.2	3.4	3.55	1.758
param Nb3+5	1.473	109.47	3.165	0.059	12	3.618	0	0.2	3.55	3.38	1.603
param Mo6+6	1.467	90	3.052	0.056	12	3.4	0	0.2	3.465	3.755	1.53
param Mo3+6	1.484	109.47	3.052	0.056	12	3.4	0	0.2	3.465	3.755	1.53
param Tc6+5	1.322	90	2.998	0.048	12	3.4	0	0.2	3.29	3.99	1.5
param Ru6+2	1.478	90	2.963	0.056	12	3.4	0	0.2	3.575	4.015	1.5
param Rh6+3	1.332	90	2.929	0.053	12	3.5	0	0.2	3.975	4.005	1.509
param Pd4+2	1.338	90	2.899	0.048	12	3.21	0	0.2	4.32	4	1.544
param Ag1+1	1.386	180	3.148	0.036	12	1.956	0	0.2	4.436	3.134	1.622
param Cd3+2	1.403	109.47	2.848	0.228	12	1.65	0	0.2	5.034	3.957	1.6
param In3+3	1.459	109.47	4.463	0.599	11	2.07	0	0.2	3.506	2.896	1.404
param Sn3	1.398	109.47	4.392	0.567	12	2.961	0.199	0.2	3.987	3.124	1.354
param Sb3+3	1.407	91.6	4.42	0.449	13	2.704	1.1	0.2	4.899	3.342	1.404
param Te3+2	1.386	90.25	4.47	0.398	14	2.882	0.3	0.2	5.816	3.526	1.38
param I_	1.382	180	4.5	0.339	15	2.65	0	0.2	6.822	3.762	1.333
param Xe4+4	1.267	90	4.404	0.332	12	0.556	0	0.2	7.595	4.975	2.459
param Cs	2.57	180	4.517	0.045	12	1.573	0	0.1	2.183	1.711	2.984
param Ba6+2	2.277	90	3.703	0.364	12	2.727	0	0.1	2.814	2.396	2.442
param La3+3	1.943	109.47	3.522	0.017	12	3.3	0	0.1	2.8355	2.7415	2.071
param Ce6+3	1.841	90	3.556	0.013	12	3.3	0	0.1	2.774	2.692	1.925
param Pr6+3	1.823	90	3.606	0.01	12	3.3	0	0.1	2.858	2.564	2.007
param Nd6+3	1.816	90	3.575	0.01	12	3.3	0	0.1	2.8685	2.6205	2.007
param Pm6+3	1.801	90	3.547	0.009	12	3.3	0	0.1	2.881	2.673	2
param Sm6+3	1.78	90	3.52	0.008	12	3.3	0	0.1	2.9115	2.7195	1.978
param Eu6+3	1.771	90	3.493	0.008	12	3.3	0	0.1	2.8785	2.7875	2.227
param Gd6+3	1.735	90	3.368	0.009	12	3.3	0	0.1	3.1665	2.9745	1.968
param Tb6+3	1.732	90	3.451	0.007	12	3.3	0	0.1	3.018	2.834	1.954
param Dy6+3	1.71	90	3.428	0.007	12	3.3	0	0.1	3.0555	2.8715	1.934
param Ho6+3	1.696	90	3.409	0.007	12	3.416	0	0.1	3.127	2.891	1.925
param Er6+3	1.673	90	3.391	0.007	12	3.3	0	0.1	3.1865	2.9145	1.915
param Tm6+3	1.66	90	3.374	0.006	12	3.3	0	0.1	3.2514	2.9329	2
param Yb6+3	1.637	90	3.355	0.228	12	2.618	0	0.1	3.2889	2.965	2.158
param Lu6+3	1.671	90	3.64	0.041	12	3.271	0	0.1	2.9629	2.4629	1.896
param Hf3+4	1.611	109.47	3.141	0.072	12	3.921	0	0.1	3.7	3.4	1.759
param Ta3+5	1.511	109.47	3.17	0.081	12	4.075	0	0.1	5.1	2.85	1.605
param W_6+6	1.392	90	3.069	0.067	12	3.7	0	0.1	4.63	3.31	1.538
param W_3+4	1.526	109.47	3.069	0.067	12	3.7	0	0.1	4.63	3.31	1.538
param W_3+6	1.38	109.47	3.069	0.067	12	3.7	0	0.1	4.63	3.31	1.538
param Re6+5	1.372	90	2.954	0.066	12	3.7	0	0.1	3.96	3.92	1.6
param Re3+7	1.314	109.47	2.954	0.066	12	3.7	0	0.1	3.96	3.92	1.6
param Os6+6	1.372	90	3.12	0.037	12	3.7	0	0.1	5.14	3.63	1.7
param Ir6+3	1.371	90	2.84	0.073	12	3.731	0	0.1	5	4	1.866
param Pt4+2	1.364	90	2.754	0.08	12	3.382	0	0.1	4.79	4.43	1.557
param Au4+3	1.262	90	3.293	0.039	12	2.625	0	0.1	4.894	2.586	1.618
param Hg1+2	1.34	180	2.705	0.385	12	1.75	0	0.1	6.27	4.16	1.6
param Tl3+3	1.518	120	4.347	0.68	11	2.068	0	0.1	3.2	2.9	1.53
param Pb3	1.459	109.47	4.297	0.663	12	2.846	0.1	0.1	3.9	3.53	1.444
param Bi3+3	1.512	90	4.37	0.518	13	2.47	1	0.1	4.69	3.74	1.514
param Po3+2	1.5	90	4.709	0.325	14	2.33	0.3	0.1	4.21	4.21	1.48
param At	1.545	180	4.75	0.284	15	2.24	0	0.1	4.75	4.75	1.47
param Rn4+4	1.42	90	4.765	0.248	16	0.583	0	0.1	5.37	5.37	2.2
param Fr	2.88	180	4.9	0.05	12	1.847	0	0	2	2	2.3
param Ra6+2	2.512	90	3.677	0.404	12	2.92	0	0	2.843	2.434	2.2
param Ac6+3	1.983	90	3.478	0.033	12	3.9	0	0	2.835	2.835	2.108
param Th6+4	1.721	90	3.396	0.026	12	4.202	0	0	3.175	2.905	2.018
param Pa6+4	1.711	90	3.424	0.022	12	3.9	0	0	2.985	2.905	1.8
param U_6+4	1.684	90	3.395	0.022	12	3.9	0	0	3.341	2.853	1.713
param Np6+4	1.666	90	3.424	0.019	12	3.9	0	0	3.549	2.717	1.8
param Pu6+4	1.657	90	3.424	0.016	12	3.9	0	0	3.243	2.819	1.84
param Am6+4	1.66	90	3.381	0.014	12	3.9	0	0	2.9895	3.0035	1.942
param Cm6+3	1.801	90	3.326	0.013	12	3.9	0	0	2.8315	3.1895	1.9
param Bk6+3	1.761	90	3.339	0.013	12	3.9	0	0	3.1935	3.0355	1.9
param Cf6+3	1.75	90	3.313	0.013	12	3.9	0	0	3.197	3.101	1.9
param Es6+3	1.724	90	3.299	0.012	12	3.9	0	0	3.333	3.089	1.9
param Fm6+3	1.712	90	3.286	0.012	12	3.9	0	0	3.4	3.1	1.9
param Md6+3	1.689	90	3.274	0.011	12	3.9	0	0	3.47	3.11	1.9
param No6+3	1.679	90	3.248	0.011	12	3.9	0	0	3.475	3.175	1.9
param Lw6+3	1.698	90	3.236	0.011	12	3.9	0	0	3.5	3.2	1.9 `;
var eric_uffparam = {};
var tmpj = table_uffparam.trim().split('\n');
for (let i=0; i<tmpj.length; ++i) {
   let ss = tmpj[i].split(/\s+/);
   eric_uffparam[ss[1]] = [ss[1],eval(ss[2]),eval(ss[3]),eval(ss[4]),eval(ss[5]),eval(ss[6]),eval(ss[7]),eval(ss[8]),eval(ss[9]),eval(ss[10]),eval(ss[11]),eval(ss[12]),Math.cos(eval(ss[3])*Math.PI/180.0)];
}


function rotatepath(path,head) {
   let n = path.indexOf(head);
   //let p = path[n:]+path[:n]
   let p = path.slice(n).concat(path.slice(0,n));
   return p;
}

function addCycles(cycles1,cycles2) {
   let cycles = cycles1;
   for (const p2 of cycles2) {
      let n = p2.indexOf(Math.min(...p2));
      //let p = p2[n:]+p2[:n]
      let p = p2.slice(n).concat(p2.slice(0,n));

      //let pinv = p[::-1]
      let pinv = p.reverse();
      n = pinv.indexOf(Math.min(...pinv));
      //pinv = pinv[n:]+pinv[:n]
      pinv = pinv.slice(n).concat(pinv.slice(0,n));
      if ((!cycles.includes(p)) && (!cycles.includes(pinv))) {
         cycles.push(p)
      }
   }

   return cycles;
}


function findCycles0(nion,amatrix,path) {
   let start_node = path[0];
   let cycles  = [];

   for (let j=0; j<nion; ++j) {
      if (amatrix[start_node+j*nion] > 0) {
         let next_node = j;
         if (!path.includes(next_node)) {
            let subpath = [next_node].concat(path)
            cycles2 = findCycles0(nion,amatrix,subpath);
            cycles  = addCycles(cycles,cycles2);
         } else if ((path.length>2) && (next_node==path[path.length-1])) {
            cycles = addCycles(cycles,[path]);
         }
      }
   }
   return cycles;
}

function findCycles(nion,amatrix,start) {
    let cycles  = []
    let cycles0 = findCycles0(nion,amatrix,[start]);
    for (p0 of cycles0) {
       cycles.push(rotatepath(p0,start));
    }

    return cycles;
}

function numberbonds(nion,amatrix,ii) {
   let nb = 0;
   for (let jj=0; jj<nion; ++jj) {
      if (jj!=ii) {
         nb += amatrix[ii+jj*nion];
      }
   }
   return Math.floor(nb+0.5);
}

function numberconnections(nion,amatrix,ii) {
   let nc = 0;
   for (let jj=0; jj<nion; ++jj) {
      if (jj!=ii) {
         if (amatrix[ii+jj*nion]>0) {
            nc += 1;
         }
      }
   }
   return nc;
}


function isneighborSP2(nion,symbols,amatrix,start) {
   let sp2 = false;
   for (j=0; j<nion; ++j) {
      if (amatrix[start+j*nion]>0) {
         let nc = numberconnections(nion,amatrix,j);
         let nb = numberbonds(nion,amatrix,j);
         let qq = amatrix[j+j*nion];
         if ((nc==3) && (nb==4) && (qq==0)) {
           sp2 = true;
         }
      }
   }
   return sp2;
}

function isSP2(nion,symbols,amatrix,start) {
   let sp2 = false;
   let sy = symbols[start];
   let qq = amatrix[start+start*nion];
   let nc = numberconnections(nion,amatrix,start);
   let nb = numberbonds(nion,amatrix,start);

   if ((sy=="B") && (nc==3) && (nb==3) && (qq==0)) {sp2 = true;}

   if ((sy=="C") && (nc==3) && (nb==4) && (qq==0))  {sp2 = true; }
   if ((sy=="C") && (nc==3) && (nb==3) && (qq==-1)) {sp2 = true; }
   if ((sy=="C") && (nc==2) && (nb==3) && (qq==+1)) {sp2 = true; }

   if ((sy=="N") && (nc==2) && (nb==3) && (qq==0)) {sp2 = true; }
   if ((sy=="N") && (nc==3) && (nb==5) && (qq==0)) {sp2 = true; }

   if ((sy=="P") && (nc==2) && (nb==3) && (qq==0)) {sp2 = true; }
   if ((sy=="P") && (nc==3) && (nb==3) && (qq==0)) {sp2 = true; }
   if ((sy=="P") && (nc==3) && (nb==5) && (qq==0)) {sp2 = true; }

   if ((sy=="O") && (nc==2) && (nb==2) && (qq==0)) {sp2 = true; }
   if ((sy=="S") && (nc==2) && (nb==2) && (qq==0)) {sp2 = true; }
   if ((sy=="Se") && (nc==2) && (nb==2) && (qq==0)) {sp2 = true; }

   return sp2;
}

function picountaromatic(nion,symbols,amatrix,start) {
   const sy = symbols[start];
   const qq = amatrix[start+start*nion];
   const nc = numberconnections(nion,amatrix,start);
   const nb = numberbonds(nion,amatrix,start);
   let npi = 0
   if ((sy=="B") && (nc==3) && (nb==3) && (qq==-1)) {npi = 1;}

   if ((sy=="C") && (nc==3) && (nb==4) && (qq==0))  {npi = 1;}
   if ((sy=="C") && (nc==2) && (nb==3) && (qq==1))  {npi = 1;}
   if ((sy=="C") && (nc==3) && (nb==3) && (qq==-1)) {npi = 1;}

   if ((sy=="N") && (nc==2) && (nb==3) && (qq==0))  {npi = 1;}
   if ((sy=="N") && (nc==3) && (nb==5) && (qq==0))  {npi = 1;}

   if ((sy=="P") && (nc==2) && (nb==3) && (qq==0))  {npi = 1;}
   if ((sy=="P") && (nc==3) && (nb==3) && (qq==0))  {npi = 2;}
   if ((sy=="P") && (nc==3) && (nb==5) && (qq==0))  {npi = 1;}

   if ((sy=="O") && (nc==2) && (nb==2) && (qq==0))  {npi = 2;}
   if ((sy=="S") && (nc==2) && (nb==2) && (qq==0))  {npi = 2;}
   if ((sy=="Se") && (nc==2) && (nb==2) && (qq==0)) {npi = 2;}

   return npi;
}

function isaromatic(nion,symbols,amatrix,start) {
   let aromatic = false;
   const cycles = findCycles(nion,amatrix,start);
   for (const path of cycles) {
      let npi = 0;
      let sp2 = true;
      for (const i of path) {
         sp2 = (sp2 && isSP2(nion,symbols,amatrix,i));
         npi += picountaromatic(nion,symbols,amatrix,i);
      }
      if ((((npi/2)%2)==1) && sp2) {aromatic=true;}
   }
   return aromatic;
}

function packindx(n,i,j) {
   var k;
   if (i<=j) {
      k = j + (2*n-1-i)*i/2;
   } else {
      k = i + (2*n-1-j)*j/2;
   }
   return k;
}

/********************************************
 *                                          *
 *              uff_KIJK                    *
 *                                          *
 ********************************************/

function uff_KIJK(nion,nkatom_type,katom,uffparam_type,preuff,border_matrix,i,j,k) {
   let bij = border_matrix[i+j*nion];
   let bjk = border_matrix[j+k*nion];
   let rij = preuff[packindx(nkatom_type,katom[i],katom[j])][1+bij];
   let rjk = preuff[packindx(nkatom_type,katom[j],katom[k])][1+bjk];
   let beta    = 664.12/(rij*rjk);
   let ctheta0 = uffparam_type[katom[j]][12];
   let Zi = uffparam_type[katom[i]][6];
   let Zk = uffparam_type[katom[k]][6];
   let rik = Math.sqrt(rij*rij+rjk*rjk-2.0*rij*rjk*ctheta0);
   
   let prefactor = beta*Zi*Zk/rik**5;
   let rterm = rij*rjk;
   let innerbit = 3.0*rterm*(1.0-ctheta0*ctheta0)-rik*rik*ctheta0;
   let KIJK = prefactor*rterm*innerbit;

   return KIJK;
}


/********************************************
 *                                          *
 *           uff_torsion_KIJKL              *
 *                                          *
 ********************************************/
function uff_torsion_KIJKL(nion,nkatom_type,katom,uffparam_type,preuff,bordermatrix,i,j,k,l) {
   const bjk = bordermatrix[j+k*nion];
   const indx = packindx(nkatom_type,katom[j],katom[k]);
   const ufftypei = uffparam_type[katom[i]][0];
   const ufftypej = uffparam_type[katom[j]][0];
   const ufftypek = uffparam_type[katom[k]][0];
   const ufftypel = uffparam_type[katom[l]][0];
   const group6j = ((ufftypej.slice(0,2)=="O_") || (ufftypej.slice(0,2)=="S_") || (ufftypej.slice(0,2)=="Se") || (ufftypej.slice(0,2)=="Te") || (ufftypej.slice(0,2)=="Po"));
   const group6k = ((ufftypek.slice(0,2)=="O_") || (ufftypek.slice(0,2)=="S_") || (ufftypek.slice(0,2)=="Se") || (ufftypek.slice(0,2)=="Te") || (ufftypek.slice(0,2)=="Po"));
   const group6 = (group6j && group6k);
   let hybridi = '';
   let hybridj = '';
   let hybridk = '';
   let hybridl = '';
   if (ufftypei.length > 2) {hybridi = ufftypei[2];}
   if (ufftypej.length > 2) {hybridj = ufftypej[2];}
   if (ufftypek.length > 2) {hybridk = ufftypek[2];}
   if (ufftypel.length > 2) {hybridl = ufftypel[2];}

   const sp2i = ((hybridi=='2') || (hybridi=='R'));
   const sp2j = ((hybridj=='2') || (hybridj=='R'));
   const sp2k = ((hybridk=='2') || (hybridk=='R'));
   const sp2l = ((hybridl=='2') || (hybridl=='R'));

   const sp3i = (hybridi=='3');
   const sp3j = (hybridj=='3');
   const sp3k = (hybridk=='3');
   const sp3l = (hybridl=='3');

   const sp2_sp2 = (sp2j && sp2k);
   const sp3_sp3 = (sp3j && sp3k);
   const sp3_sp2 = ((sp3j && sp2k) || (sp2j && sp3k));
   const sp3_sp2_sp2 = ((sp3j && sp2k && sp2l) || (sp2i && sp2j && sp3k));

   var V,n,cnphi0;
   if (sp3_sp3) {
      V      = preuff[indx][12];
      cnphi0 = -1.0;
      n = 3;

      if (group6 && (bjk==1)) {
         let V2=6.8;
         let V3=6.8;
         if (ufftypej.slice(0,2)=="O_") {V2=2.0;}
         if (ufftypek.slice(0,2)=="O_") {V3=2.0;}
         V      = Math.sqrt(V2*V3);
         cnphi0 = -1.0;
         n = 2;
      }

   } else if (sp2_sp2) {
         V      = preuff[indx][12+bjk];
         cnphi0 = 1.0;
         n = 2;
   } else {
      V      = 1.0;
      cnphi0 = 1.0;
      n = 6;
      if (bjk==1) {
         if ((group6j && sp3j && sp2k && (!group6k)) || (group6k && sp3k && sp2j && (!group6j))) {
            V      = preuff[indx][12+bjk];
            cnphi0 = -1.0;
            n = 2;
         } else if (sp3_sp2_sp2) {
            V      = 2.0;
            cnphi0 = -1.0;
            n = 3;
         }
      }
   }

   return [V,n,cnphi0];
}


/********************************************
 *                                          *
 *           uff_inversion_KIJKL            *
 *                                          *
 ********************************************/
function uff_inversion_KIJKL(katom,uffparam_type,i,j,k,l) {
   const ufftype = uffparam_type[katom[j]][0];
   let C0 = 0.0;
   let C1 = 0.0;
   let C2 = 0.0;
   let KIJKL = 0.0;
   if ((ufftype=='C_2') || (ufftype=='C_R')) {
      C0 = 1.0;
      C1 = -1.0;
      C2 = 0.0;
      const ufftypei = uffparam_type[katom[i]][0];
      const ufftypek = uffparam_type[katom[k]][0];
      const ufftypel = uffparam_type[katom[l]][0];
      if ((ufftypei=="O_2") || (ufftypek=="O_2") || (ufftypel=="O_2")) {
         KIJKL = 50.0;
      } else {
         KIJKL = 6.0;
      }
   } else if ((ufftype.slice(0,2)=='N_') || (ufftype.slice(0,2)=='O_')) {
      C0 = 1.0;
      C1 = -1.0;
      C2 = 0.0;
      KIJKL = 6.0;
   } else if (ufftype.slice(0,2)=='P_') {
      const w0 = Math.PI/180.0 * 84.4339;
      C2 = 1.0;
      C1 = -4.0*Math.cos(w0);
      C0 = -(C1*Math.cos(w0) + C2*Math.cos(2.0*w0));
      KIJKL = 22.0/(3*(C0+C1+C2));
   } else if (ufftype.slice(0,2)=='As') {
      const w0 = Math.PI/180.0 * 86.9735;
      C2 = 1.0;
      C1 = -4.0*Math.cos(w0);
      C0 = -(C1*Math.cos(w0) + C2*Math.cos(2.0*w0));
      KIJKL = 22.0/(3*(C0+C1+C2));
   } else if (ufftype.slice(0,2)=='Sb') {
      const w0 = Math.PI/180.0 * 87.7047;
      C2 = 1.0;
      C1 = -4.0*Math.cos(w0);
      C0 = -(C1*Math.cos(w0) + C2*Math.cos(2.0*w0));
      KIJKL = 22.0/(3*(C0+C1+C2));
   } else if (ufftype.slice(0,2)=='Bi') {
      const w0 = Math.PI/180.0 * 90.0;
      C2 = 1.0;;
      C1 = -4.0*Math.cos(w0);
      C0 = -(C1*Math.cos(w0) + C2*Math.cos(2.0 * w0));
      KIJKL = 22.0/(3*(C0+C1+C2));
   }

   return [KIJKL,C0,C1,C2];
}






class UFF_Potential {
   constructor(nion,symbol,amatrix) {

      this.mdlat  = [];
      this.nshl3d = 1;
      this.rcell  = [0.0,0.0,0.0];

      this.neighbors1 = [];
      for (let i=0; i<nion; ++i) {
         let ineighbors = [];
         for (let j=0; j<nion; ++j) {
            if ((amatrix[i+j*nion]>0) && (i!=j)) {
               ineighbors.push(j);
            }
         }
         this.neighbors1.push(ineighbors);
      }

      this.neighbors12 = [];
      for (let i=0; i<nion; ++i) {
         let ineighbors = []
         ineighbors = ineighbors.concat(this.neighbors1[i]);
         for (let j=0; j<this.neighbors1[i].length; ++j) {
            ineighbors = ineighbors.concat(this.neighbors1[this.neighbors1[i][j]]);
         }
         this.neighbors12.push(Array.from(new Set(ineighbors)));
      }
      
      //console.log("SYMBOL=",symbol);
      //console.log("charge SYMBOL=",eric_periodic_table_charge[symbol[1]] );

      /* figure out UFF atom types */
      this.isaromatictype = [];
      this.atype = [];
      this.ufftype = [];
      for (let ii=0; ii<nion; ++ii) {
         let qq = amatrix[ii+ii*nion];
         let nb = numberbonds(nion,amatrix,ii);
         let nc = numberconnections(nion,amatrix,ii);
         let at = false;
         var aa;

         if (eric_periodic_table_charge[symbol[ii]]==1) {
            if (nb>1) {
               aa = "[#1D2]";
            } else {
               aa = "[#1]";
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==5) {
            if (nb==4) {
               aa = "[#5D4]"
            } else {
               aa = "[#5]"
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==6) {
            aa = "[#6]";
            if ((nc==4) && (nb==4) && (qq==0)) {
               aa = "[#6]";
            } else if ((nc==3) && (nb==4) && (qq==0)) {
               if (isaromatic(nion,symbol,amatrix,ii)) {
                  aa = "[c]"; 
                  at = true;
               } else {
                  aa = "[C^2]";
               }
            } else if ((nc==3) && (nb==3)) {
               if (isneighborSP2(nion,symbol,amatrix,ii)) {
                  aa = "[CA1]";
               } else if (qq==+1) {
                  aa = "[C+1]";
               } else {
                  aa = "[C-1]";
               }
            } else if ((nc==2) && (nb==4) && (qq==0)) {
               aa = "[C^1]";
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==7) {
            aa = "[#7]";
            if ((nc==3) && (nb==3) && (qq==0)) {
               aa = "[#7]";
            } else if ((nc==2) && (nb==3) && (qq==0)) {
               if (isaromatic(nion,symbol,amatrix,ii)) {
                  aa = "[n]";
                  at = true;
               } else {
                  aa = "[N^2]"; 
               }
            } else if ((nc==3) && (nb==4) && (qq==0)) {
               aa = "[N^2]"
            } else if ((nc==1) && (nb==3) && (qq==0)) {
               aa = "[N^1]"
            }

         } else if (eric_periodic_table_charge[symbol[ii]]==8) {
            aa = "[#8]";
            if ((nc==1) && (nb==2) && (qq==0)) {
               aa = "[O^2]";
            } else if ((nc==2) && (nb==2) && (qq==0)) {
               if (isaromatic(nion,symbol,amatrix,ii)) {
                  aa = "[o]"; 
                  at = true;
               } else {
                  aa = "[#8]";
               }
            }

         } else if (eric_periodic_table_charge[symbol[ii]]==15) {
            aa = "[#15]";
            if ((nc==3) && (nb==3) && (qq==0)) {
               aa = "[#15]";
            } else if ((nc==2) && (nb==3) && (qq==0)) {
               if (isaromatic(nion,symbol,amatrix,ii)) {
                  aa = "[p]"; 
                  at = true;
               } else {
                  aa = "[P^2]";
               }
            } else if ((nc==3) && (nb==4) && (qq==0)) {
               aa = "[P^2]";
            } else if ((nc==1) && (nb==3) && (qq==0)) {
               aa = "[P^1]";
            }

         } else if (eric_periodic_table_charge[symbol[ii]]==16) {
            aa = "[#16]";
            if ((nc==1) && (nb==2) && (qq==0)) {
               aa = "[S^2]";
            } else if ((nc==2) && (nb==2) && (qq==0)) {
               if (isaromatic(nion,symbol,amatrix,ii)) {
                  aa = "[s]"; 
                  at = true;
               } else {
                  aa = "[#16]";
               }
            }

         } else if (eric_periodic_table_charge[symbol[ii]]==22) {
            if (nb==4) {
               aa = "[#22D3]";
            } else {
               aa = "[#22]";
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==26) {
            if (nb==4) {
               aa = "[#26D3]";
            } else {
               aa = "[#26]";
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==42) {
            if (nb==4) {
               aa = "[#42D3]";
            } else {
               aa = "[#42]";
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==74) {
            if (nb==4) {
               if (qq==6) {
                  aa = "[#74D3+6]";
               } else {
                  aa = "[#74D3+4]";
               }
            } else {
               aa = "[#74]";
            }
         } else if (eric_periodic_table_charge[symbol[ii]]==75) {
            if (nb==4) {
               aa = "[#75D3]";
            } else {
               aa = "[#75]";
            }
         } else {
            aa = sprintf("[#%d]",eric_periodic_table_charge[symbol[ii]]);
         }
         this.atype.push(aa);
         this.ufftype.push(eric_smartuff[aa]);
         this.isaromatictype.push(at);
      }

      //console.log("UFFTYPE=",this.ufftype);

      /* adjust amatrix to aromatic bondorders */
      let border_matrix = [...amatrix];
      for (let i=0; i<(nion-1); ++i) {
         for (let j=i+1; j<nion; ++j) {
            if ((((border_matrix[i+j*nion]>=1)&&(border_matrix[i+j*nion]<=2))&&((this.isaromatictype[i])&&(this.isaromatictype[j])))||(border_matrix[i+j*nion]==1.5)) {
               border_matrix[i+j*nion] = 5;
               border_matrix[j+i*nion] = 5;
            }
         }
      }

      /* define katom */
      let katom_type   = Array.from(new Set(this.ufftype)); 
      this.nkatom_type = katom_type.length;
      this.katom = [];
      for (let i=0; i<nion; ++i) {
         let k = katom_type.indexOf(this.ufftype[i]);
         this.katom.push(k);
      }

      /* fetch uff param data for each kind of atom */
      let uffparam_type = [];
      for (let i=0; i<this.nkatom_type; ++i ) {
         uffparam_type.push(eric_uffparam[katom_type[i]]);
      }

      /*  generate spring constants, distances, angle potential constants,... using uff param data  */
      /*param Atom    r1      theta0  x1      D1      zeta    Z1      Vi      Uj      Xi      Hard    Radius */
      this.preuff = [];
      for (let i=0; i<this.nkatom_type; ++i) {
         const iparam = uffparam_type[i];
         const ri     = iparam[1];
         const thetai = iparam[2];
         const xi = iparam[3];
         const Di = iparam[4];
         const Zi = iparam[6];
         const Vi = iparam[7];
         const Ui = iparam[8];
         const Chii = iparam[9];
         for (let j=i; j<this.nkatom_type; ++j) {
            const jparam = uffparam_type[j];
            const rj     = jparam[1];
            const thetaj = jparam[2];
            const xj = jparam[3];
            const Dj = jparam[4];
            const Zj = jparam[6];
            const Vj = jparam[7];
            const Uj = jparam[8];
            const Chij = jparam[9];

            let rEN = ri * rj * (Math.sqrt(Chii) - Math.sqrt(Chij)) * (Math.sqrt(Chii) -Math.sqrt(Chij))/(Chii*ri + Chij*rj);

            let rBO10 = -0.1332*(ri + rj)*Math.log(1.0);
            let rBO15 = -0.1332*(ri + rj)*Math.log(1.5);
            let rBO20 = -0.1332*(ri + rj)*Math.log(2.0);
            let rBO30 = -0.1332*(ri + rj)*Math.log(3.0);
            let rBO40 = -0.1332*(ri + rj)*Math.log(4.0);

            let rij10 = ri + rj + rBO10 - rEN;
            let rij15 = ri + rj + rBO15 - rEN;
            let rij20 = ri + rj + rBO20 - rEN;
            let rij30 = ri + rj + rBO30 - rEN;
            let rij40 = ri + rj + rBO40 - rEN;

            let kij10 = 664.12*Zi*Zj/(rij10**3);
            let kij15 = 664.12*Zi*Zj/(rij15**3);
            let kij20 = 664.12*Zi*Zj/(rij20**3);
            let kij30 = 664.12*Zi*Zj/(rij30**3);
            let kij40 = 664.12*Zi*Zj/(rij40**3);

            let Vsp3 = Math.sqrt(Vi*Vj);
            let Vsp2_10 = 5*Math.sqrt(Ui*Uj)*(1.0+4.18*Math.log(1.0));
            let Vsp2_15 = 5*Math.sqrt(Ui*Uj)*(1.0+4.18*Math.log(1.5));
            let Vsp2_20 = 5*Math.sqrt(Ui*Uj)*(1.0+4.18*Math.log(2.0));
            let Vsp2_30 = 5*Math.sqrt(Ui*Uj)*(1.0+4.18*Math.log(3.0));
            let Vsp2_40 = 5*Math.sqrt(Ui*Uj)*(1.0+4.18*Math.log(4.0));

            //print "Vs=",Vi,Vj,Ui,Uj," --> ",Vsp3,Vsp2_10,Vsp2_15,Vsp2_20,Vsp2_30,Vsp2_40
            //print "    --> ",Math.sqrt(Ui*Uj),5*(1+4.18*Math.log(1.5))

            let xij = 0.5*(xi+xj);
            let Dij = Math.sqrt(Di*Dj);

            let data = [Dij,xij,rij10,rij20,rij30,rij40,rij15,kij10,kij20,kij30,kij40,kij15,Vsp3,Vsp2_10,Vsp2_20,Vsp2_30,Vsp2_40,Vsp2_15];
            this.preuff.push(data)
         }
      }

      /* set up bondstretch potentials */
      this.bondstretch = [];
      for (let i=0; i<(nion-1); ++i) {
         for (let j=i+1; j<nion; ++j) {
            let bij = border_matrix[i+j*nion];
            if (bij>0) {
               let rij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][1+bij];
               let kij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][6+bij];
               this.bondstretch.push([i,j,rij,kij]);
            } else if (bij<-10) {
               let rij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][1+1];
               let kij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][6+1];
               this.bondstretch.push([i,j,rij,kij]);
            }
         }
      }

      /* set up anglebend potentials */
      this.anglebend = [];
      for (let j=0; j<nion; ++j) {
         let ctheta0 = uffparam_type[this.katom[j]][12];
         let atype   = uffparam_type[this.katom[j]][0];
         let hybridization = 0;
         if (atype.length>2) {
            if (atype[2]=='1')  {hybridization=1;}
            if (atype[2]=='2')  {hybridization=3;}
            if (atype[2]=='4')  {hybridization=4;}
            if (atype[2]=='6')  {hybridization=4;}
            if (atype=="Bi3+3")  {hybridization=2;}
            if (atype=="Po3+3")  {hybridization=2;}
         }
         let ic = 0;
         for (let i of this.neighbors1[j]) {
            for (let k of this.neighbors1[j].slice(ic+1)) {
               let KIJK = uff_KIJK(nion,this.nkatom_type,this.katom,uffparam_type,this.preuff,border_matrix,i,j,k)
               this.anglebend.push([i,j,k,hybridization,KIJK,ctheta0]);
            }
            ic += 1;
         }
      }

      /* set up torsion potentials */
      this.torsion = [];
      for (let j=0; j<(nion-1); ++j) {
         for (let k=j+1; k<nion; ++k) {
            if ((amatrix[j+k*nion]>0) && (j!=k)) {
               for (const i of this.neighbors1[j]) {
                  if ((i!=j) && (i!=k)) {
                     for (const l of this.neighbors1[k]) {
                        if ((l!=i) && (l!=j) && (l!=k)) {
                           //tor = (V,n,cnphi) 
                           let tor = uff_torsion_KIJKL(nion,this.nkatom_type,this.katom,uffparam_type,this.preuff,border_matrix,i,j,k,l);
                           this.torsion.push([i,j,k,l,tor[0],tor[1],tor[2]]);
                        }
                     }
                  }
               }
            }
         }
      }

      /* set up inversion potentials */
      this.inversion = [];
      for (let i=0; i<nion; ++i) {
         let ic = 0;
         for (const j of this.neighbors1[i]) {
            let ic2 = 0;
            for (const k of this.neighbors1[i].slice(ic+1)) {
               for (const l of this.neighbors1[i].slice(ic+ic2+2)) {
                  // uinv = (KIJKL,C0,C1,C2) 
                  let uinv = uff_inversion_KIJKL(this.katom,uffparam_type,i,j,k,l);
                  if (Math.abs(uinv[0])>1.0e-6) {
                     this.inversion.push([i,j,k,l,uinv[0],uinv[1],uinv[2],uinv[3]]);
                  }
               }
               ic2 += 1
            }
            ic += 1;
         }
      }

   } /* end constructor */

   /*****************************
    *       mdlat               *
    *****************************/
   mdlat_setter(a1,a2,a3) {
      let  b1 = [a2[1]*a3[2]-a2[2]*a3[1], a2[2]*a3[0]-a2[0]*a3[2], a2[0]*a3[1]-a2[1]*a3[0]];
      let  b2 = [a3[1]*a1[2]-a3[2]*a1[1], a3[2]*a1[0]-a3[0]*a1[2], a3[0]*a1[1]-a3[1]*a1[0]];
      let  b3 = [a1[1]*a2[2]-a1[2]*a2[1], a1[2]*a2[0]-a1[0]*a2[2], a1[0]*a2[1]-a1[1]*a2[0]];
      let vol = a1[0]*b1[0] + a1[1]*b1[1] + a1[2]*b1[2];
      b1[0] /= vol; b1[1] /= vol; b1[2] /= vol;
      b2[0] /= vol; b2[1] /= vol; b2[2] /= vol;
      b3[0] /= vol; b3[1] /= vol; b3[2] /= vol;
      this.mdlat = [a1,a2,a3,b1,b2,b3];

      this.nshl3d = 1;
      this.rcell  = [0.0,0.0,0.0];
      for (let n3=-2; n3<3; ++n3) {
         for (let n2=-2; n2<3; ++n2) {
            for (let n1=-2; n1<3; ++n1) {
               if (!((n3==0) && (n2==0) && (n1==0))) {
                  let xx = (n1*a1[0] + n2*a2[0] + n3*a3[0]);
                  let yy = (n1*a1[1] + n2*a2[1] + n3*a3[1]);
                  let zz = (n1*a1[2] + n2*a2[2] + n3*a3[2]);
                  let r = Math.sqrt(xx*xx + yy*yy + zz*zz);
                  if (r<25.0) {
                     this.rcell.push(xx);
                     this.rcell.push(yy);
                     this.rcell.push(zz);
                     this.nshl3d += 1; 
                  }
               }
            }
         }
      }
   }

   mdlat_min_diff(dx,dy,dz) {
      if (this.mdlat.length==6) {
         let c0 = this.mdlat[3][0]*dx + this.mdlat[3][1]*dy + this.mdlat[3][2]*dz;
         let c1 = this.mdlat[4][0]*dx + this.mdlat[4][1]*dy + this.mdlat[4][2]*dz;
         let c2 = this.mdlat[5][0]*dx + this.mdlat[5][1]*dy + this.mdlat[5][2]*dz;
         c0 = c0 - Math.round(c0);
         c1 = c1 - Math.round(c1);
         c2 = c2 - Math.round(c2);
         return [c0*this.mdlat[0][0] + c1*this.mdlat[1][0] + c2*this.mdlat[2][0],
                 c0*this.mdlat[0][1] + c1*this.mdlat[1][1] + c2*this.mdlat[2][1],
                 c0*this.mdlat[0][2] + c1*this.mdlat[1][2] + c2*this.mdlat[2][2]];
      } else {
         return [dx,dy,dz];
      }
   }

   /*****************************
    *       Bond Stretch        *
    *****************************/
   bondstretch_e(nion,rion) {
      let E = 0.0;
      for (const bs of this.bondstretch) {
         const i   = bs[0];
         const j   = bs[1];
         const rij = bs[2];
         const kij = bs[3];
         
         let [dx,dy,dz] = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         let r = Math.sqrt(dx*dx + dy*dy + dz*dz);
         E += 0.5*kij*(r-rij)**2;
      }
      return E;
   }

   bondstretch_egrad(nion,rion) {
      let E    = 0.0;
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0};
      for (const bs of this.bondstretch) {
         const i   = bs[0];
         const j   = bs[1];
         const rij = bs[2];
         const kij = bs[3];
         
         let [dx,dy,dz] = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         const r = Math.sqrt(dx*dx + dy*dy + dz*dz);
         E += 0.5*kij*(r-rij)**2;
         const dedr = kij*(r-rij);
         grad[3*i]   += dedr*(dx/r);
         grad[3*i+1] += dedr*(dy/r);
         grad[3*i+2] += dedr*(dz/r);
         grad[3*j]   -= dedr*(dx/r);
         grad[3*j+1] -= dedr*(dy/r);
         grad[3*j+2] -= dedr*(dz/r);
      }
      return [E,grad];
   }

   /*****************************
    *       static methods      *
    *****************************/
   vdot3(a,b) {
      let c = [0.0, 0.0, 0.0];
      c[0] = a[1]*b[2] - a[2]*b[1];
      c[1] = a[2]*b[0] - a[0]*b[2];
      c[2] = a[0]*b[1] - a[1]*b[0];
      return c;
   }

   ddot3(a,b) {
      let d = a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
      return d;
   }

   /*****************************
    *       Angle Bend          *
    *****************************/
   anglebend_e(nion,rion) {
      let E = 0.0;
      for (const ab of this.anglebend) {
         const i = ab[0];
         const j = ab[1];
         const k = ab[2];
         const anglefunc = ab[3];
         const KIJK      = ab[4];
         const ctheta0   = ab[5];

         let [dxij,dyij,dzij] = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         const rijsq = (dxij*dxij + dyij*dyij + dzij*dzij);
         const rij   = Math.sqrt(rijsq);

         let [dxkj,dykj,dzkj] = this.mdlat_min_diff(rion[3*k]-rion[3*j],rion[3*k+1]-rion[3*j+1],rion[3*k+2]-rion[3*j+2]);
         const rkjsq =(dxkj*dxkj + dykj*dykj + dzkj*dzkj);
         const rkj = Math.sqrt(rkjsq);
         const denom = rij*rkj;
         if (denom>1.0e-11) {
            let ctheta = (dxij*dxkj + dyij*dykj + dzij*dzkj)/(denom);
            if (ctheta>1.0)  {ctheta = 1.0;}
            if (ctheta<-1.0) {ctheta = -1.0;}
            let stheta = Math.sqrt(1.0 - ctheta**2);

            /* linear coordination min=180 degrees */
            if (anglefunc==1) {
               E += KIJK*(1.0+ctheta);

            /* perpendicular coordination? min=90 degrees */
            } else if (anglefunc==2) {
               let c2theta = ctheta**2 - stheta**2;
               E += (0.25*KIJK)*(1.0+c2theta);

            /* trigonal planar coordinationmin=120 degrees  */
            } else if (anglefunc==3) {
               let c3theta = ctheta**3 - 3*ctheta*stheta**2;
               E += (KIJK/9.0)*(1.0-c3theta);

            /* square planar or octahdral coordination min=90 degrees */
            } else if (anglefunc==4) {
               let c4theta = ctheta**4 - 6*ctheta**2*stheta**2 + stheta**4;
               E += (KIJK/16.0)*(1.0-c4theta);
            /* general angles */
            } else {
               let c2theta = ctheta**2 - stheta**2;
               let C2 = 1.0/(4.0*(1.0-ctheta0*ctheta0));
               let C1 = -4.0*C2*ctheta0;
               let C0 = C2*(2.0*ctheta0**2 + 1.0);
               E += KIJK*(C0 + C1*ctheta + C2*c2theta);
            }
         }
      }
      return E;
   }

   anglebend_egrad(nion,rion) {
      let E = 0.0;
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0;}
      for (const ab of this.anglebend) {
         const i = ab[0];
         const j = ab[1];
         const k = ab[2];
         const anglefunc = ab[3];
         const KIJK      = ab[4];
         const ctheta0   = ab[5];

         let [dxij,dyij,dzij] = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         const rijsq = (dxij*dxij + dyij*dyij + dzij*dzij);
         const rij   = Math.sqrt(rijsq);

         let [dxkj,dykj,dzkj] = this.mdlat_min_diff(rion[3*k]-rion[3*j],rion[3*k+1]-rion[3*j+1],rion[3*k+2]-rion[3*j+2]);
         const rkjsq =(dxkj*dxkj + dykj*dykj + dzkj*dzkj);
         const rkj = Math.sqrt(rkjsq);
         const denom = rij*rkj;

         if (denom>1.0e-11) {
            let ctheta = (dxij*dxkj + dyij*dykj + dzij*dzkj)/(denom);
            if (ctheta>1.0)  {ctheta = 1.0;}
            if (ctheta<-1.0) {ctheta = -1.0;}
            const stheta = Math.sqrt(1.0 - ctheta**2);

            var dEdtheta,invstheta;

            /* linear coordination min=180 degrees */
            if   (anglefunc==1) {
               E += KIJK*(1.0+ctheta);
               dEdtheta = -KIJK*stheta;

            /* perpendicular coordination? min=90 degrees */
            } else if (anglefunc==2) {
               const c2theta = ctheta**2 - stheta**2;
               const s2theta = 2.0*stheta*ctheta;
               E += (0.25*KIJK)*(1.0+c2theta);
               dEdtheta = -0.5*KIJK*s2theta;

            /* trigonal planar coordinationmin=120 degrees  */
            } else if (anglefunc==3) {
               const c3theta = ctheta**3 - 3*ctheta*stheta**2;
               const s3theta = stheta*(3.0-4.0*stheta*stheta);
               E += (KIJK/9.0)*(1.0-c3theta);
               dEdtheta = (KIJK/3.0)*s3theta;

            /* square planar or octahdral coordination min=90 degrees */
            } else if (anglefunc==4) {
               const c4theta = ctheta**4 - 6*ctheta**2*stheta**2 + stheta**4;
               const s4theta = ctheta*stheta*(4.0-8.0*stheta*stheta);
               E += (KIJK/16.0)*(1.0-c4theta);
               dEdtheta = (KIJK/4.0)*s4theta;

            /* general angles */
            } else {
               const c2theta = ctheta**2 - stheta**2
               const s2theta = 2.0*stheta*ctheta;
               if ((Math.abs(1.0-ctheta0*ctheta0))>1e-6) {
                  const C2 = 1.0/(4.0*(1.0-ctheta0*ctheta0))
                  const C1 = -4.0*C2*ctheta0
                  const C0 = C2*(2.0*ctheta0**2 + 1.0)
                  E += KIJK*(C0 + C1*ctheta + C2*c2theta);
                  dEdtheta = -KIJK*(C1*stheta + 2.0*C2*s2theta);
               } else {
                  dEdtheta = 0.0;
               }

            }

            if (stheta<1.0e-8) {
               invstheta = 1.0/1.0e-8
            } else {
               invstheta = 1.0/stheta
            }
            const aa  = dEdtheta*invstheta;
            const a11 =  aa*ctheta/rijsq;
            const a12 = -aa/(denom);
            const a22 =  aa*ctheta/rkjsq;

            const vx1 = a11*dxij + a12*dxkj;
            const vx2 = a22*dxkj + a12*dxij;

            const vy1 = a11*dyij + a12*dykj;
            const vy2 = a22*dykj + a12*dyij;

            const vz1 = a11*dzij + a12*dzkj;
            const vz2 = a22*dzkj + a12*dzij;

            grad[3*i]   += vx1;
            grad[3*i+1] += vy1;
            grad[3*i+2] += vz1;
            grad[3*j]   -= (vx1 + vx2);
            grad[3*j+1] -= (vy1 + vy2);
            grad[3*j+2] -= (vz1 + vz2);
            grad[3*k]   += vx2;
            grad[3*k+1] += vy2;
            grad[3*k+2] += vz2;
         }
      }
      return [E,grad];
   }

   /*****************************
    *       Torsion             *
    *****************************/
   torsion_e(nion,rion) {
      let E = 0.0;
      let phi = 0.0;
      for (const tor of this.torsion) {
         const i = tor[0];
         const j = tor[1];
         const k = tor[2];
         const l = tor[3];
         const V = tor[4];
         const n = tor[5];
         const cnphi0 = tor[6];
         //E += 0.5*V*(1-cos(n*phi_0)*cos(n*phi))#

         let r12 = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         let r32 = this.mdlat_min_diff(rion[3*k]-rion[3*j],rion[3*k+1]-rion[3*j+1],rion[3*k+2]-rion[3*j+2]);
         let r34 = this.mdlat_min_diff(rion[3*k]-rion[3*l],rion[3*k+1]-rion[3*l+1],rion[3*k+2]-rion[3*l+2]);

         /* n1=b1xb2 */
         const r52 = this.vdot3(r12,r32);
         const s52 = this.ddot3(r52,r52);

         /* n2=b2xb3 */
         const r63 = this.vdot3(r32,r34);
         const s63 = this.ddot3(r63,r63);

         const s5263 = this.ddot3(r52,r63);
         const s1263 = this.ddot3(r12,r63);
         
         let cphi = s5263/Math.sqrt(s52*s63);
         if (cphi>1.0)    {cphi =  1.0;}
         if (cphi<(-1.0)) {cphi = -1.0;}
         if (s1263<0.0) {
            phi = -Math.acos(cphi);
         } else {
            phi = Math.acos(cphi);
         }
         //#sphi  = math.sin(phi)
         const cnphi = Math.cos(n*phi);

         /* removed 1/2 because duplicate torsions not included */
         //#E += 0.5*V*(1.0-cnphi0*cnphi)
         E += V*(1.0-cnphi0*cnphi);
      }
      return E;
   }

   torsion_egrad(nion,rion) {
      let E = 0.0;
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0;}
      let phi = 0.0;
      for (const tor of this.torsion) {
         const i = tor[0];
         const j = tor[1];
         const k = tor[2];
         const l = tor[3];
         const V = tor[4];
         const n = tor[5];
         const cnphi0 = tor[6];

         let r12 = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         let r32 = this.mdlat_min_diff(rion[3*k]-rion[3*j],rion[3*k+1]-rion[3*j+1],rion[3*k+2]-rion[3*j+2]);
         let r34 = this.mdlat_min_diff(rion[3*k]-rion[3*l],rion[3*k+1]-rion[3*l+1],rion[3*k+2]-rion[3*l+2]);

         const s32 = this.ddot3(r32,r32);

         /* n1=b1xb2 */
         const r52 = this.vdot3(r12,r32);
         const s52 = this.ddot3(r52,r52);

         /* n2=b2xb3 */
         const r63 = this.vdot3(r32,r34);
         const s63 = this.ddot3(r63,r63);

         const s5263 = this.ddot3(r52,r63);
         const s1263 = this.ddot3(r12,r63);
         const s1232 = this.ddot3(r12,r32);
         const s3432 = this.ddot3(r34,r32);

      
         let cphi = s5263/Math.sqrt(s52*s63);
         if (cphi>1.0)    {cphi =  1.0;}
         if (cphi<(-1.0)) {cphi = -1.0;}
         if (s1263<0.0) {
            phi = -Math.acos(cphi);
         } else {
            phi = Math.acos(cphi);
         }

         const cnphi = Math.cos(n*phi);
         const snphi = Math.sin(n*phi);

         /* removed 1/2 because duplicate torsions not included */
         E += V*(1.0-cnphi0*cnphi);
         let dEdphi = V*cnphi0*n*snphi;

         const a1 = Math.sqrt(s32)/s52;
         const a2 = Math.sqrt(s32)/s63;
         const a3 = s1232/s32;
         const a4 = s3432/s32;
         const a31 = a3*a1;
         const a31_1 = a31-a1;
         const a42 = a4*a2;
         const a42_2 = a42-a2;

         for (let s=0; s<3; ++s) {
            grad[3*i+s] += (a1*r52[s])*dEdphi;
            grad[3*j+s] += ( a31_1*r52[s] + a42*r63[s])*dEdphi;
            grad[3*k+s] += (-a42_2*r63[s] - a31*r52[s])*dEdphi;
            grad[3*l+s] += (-a2*r63[s])*dEdphi;
         }

      }
      return [E,grad];
   }

   /*****************************
    *       Inversion           *
    *****************************/
   inversion_e(nion,rion) {
      let E = 0.0;
      for (const invrt of this.inversion) {
         const i = invrt[0];
         const j = invrt[1];
         const k = invrt[2];
         const l = invrt[3];
         const KIJKL = invrt[4];
         const C0    = invrt[5];
         const C1    = invrt[6];
         const C2    = invrt[7];
 
         let [dx_ij,dy_ij,dz_ij] = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         const rij = Math.sqrt(dx_ij*dx_ij+dy_ij*dy_ij+dz_ij*dz_ij);
         dx_ij /= rij;
         dy_ij /= rij;
         dz_ij /= rij;

         let [dx_kj,dy_kj,dz_kj] = this.mdlat_min_diff(rion[3*k]-rion[3*j],rion[3*k+1]-rion[3*j+1],rion[3*k+2]-rion[3*j+2]);
         const rkj = Math.sqrt(dx_kj*dx_kj+dy_kj*dy_kj+dz_kj*dz_kj);
         dx_kj /= rkj;
         dy_kj /= rkj;
         dz_kj /= rkj;

         let [dx_lj,dy_lj,dz_lj] = this.mdlat_min_diff(rion[3*l]-rion[3*j],rion[3*l+1]-rion[3*j+1],rion[3*l+2]-rion[3*j+2]);
         const rlj = Math.sqrt(dx_lj*dx_lj+dy_lj*dy_lj+dz_lj*dz_lj);
         dx_lj /= rlj;
         dy_lj /= rlj;
         dz_lj /= rlj;

         /* n1=-(b1xb2) */
         let dx_ijk = -(dy_ij * dz_kj - dy_kj * dz_ij);
         let dy_ijk = -(dz_ij * dx_kj - dz_kj * dx_ij);
         let dz_ijk = -(dx_ij * dy_kj - dx_kj * dy_ij);
         const r_ijk = Math.sqrt(dx_ijk*dx_ijk+dy_ijk*dy_ijk+dz_ijk*dz_ijk);
         dx_ijk /= r_ijk;
         dy_ijk /= r_ijk;
         dz_ijk /= r_ijk;

         let cgamma = dx_ijk*dx_lj+dy_ijk*dy_lj+dz_ijk*dz_lj;
         if (cgamma>1.0)  {cgamma =  1.0;}
         if (cgamma<-1.0) {cgamma = -1.0;}
         const sgamma = Math.max(Math.sqrt(1.0-cgamma**2),1.0e-9);

         const c2gamma = 2.0*sgamma*sgamma-1.0

         E += KIJKL*(C0 + C1*sgamma + C2*c2gamma);

      }
      return E;
   }

   inversion_egrad(nion,rion) {
      let E = 0.0;
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0;}
      for (const invrt of this.inversion) {
         const i = invrt[0];
         const j = invrt[1];
         const k = invrt[2];
         const l = invrt[3];
         const KIJKL = invrt[4];
         const C0    = invrt[5];
         const C1    = invrt[6];
         const C2    = invrt[7];

         let [dx_ij,dy_ij,dz_ij] = this.mdlat_min_diff(rion[3*i]-rion[3*j],rion[3*i+1]-rion[3*j+1],rion[3*i+2]-rion[3*j+2]);
         const rij = Math.sqrt(dx_ij*dx_ij+dy_ij*dy_ij+dz_ij*dz_ij);
         dx_ij /= rij;
         dy_ij /= rij;
         dz_ij /= rij;

         let [dx_kj,dy_kj,dz_kj] = this.mdlat_min_diff(rion[3*k]-rion[3*j],rion[3*k+1]-rion[3*j+1],rion[3*k+2]-rion[3*j+2]);
         const rkj = Math.sqrt(dx_kj*dx_kj+dy_kj*dy_kj+dz_kj*dz_kj);
         dx_kj /= rkj;
         dy_kj /= rkj;
         dz_kj /= rkj;

         let [dx_lj,dy_lj,dz_lj] = this.mdlat_min_diff(rion[3*l]-rion[3*j],rion[3*l+1]-rion[3*j+1],rion[3*l+2]-rion[3*j+2]);
         const rlj = Math.sqrt(dx_lj*dx_lj+dy_lj*dy_lj+dz_lj*dz_lj);
         dx_lj /= rlj;
         dy_lj /= rlj;
         dz_lj /= rlj;

         /* n1=-(b1xb2) */
         let dx_ijk = -(dy_ij * dz_kj - dy_kj * dz_ij);
         let dy_ijk = -(dz_ij * dx_kj - dz_kj * dx_ij);
         let dz_ijk = -(dx_ij * dy_kj - dx_kj * dy_ij);
         const r_ijk = Math.sqrt(dx_ijk*dx_ijk+dy_ijk*dy_ijk+dz_ijk*dz_ijk);
         dx_ijk /= r_ijk;
         dy_ijk /= r_ijk;
         dz_ijk /= r_ijk;

         let cgamma = dx_ijk*dx_lj+dy_ijk*dy_lj+dz_ijk*dz_lj;
         if (cgamma>1.0)  {cgamma =  1.0;}
         if (cgamma<-1.0) {cgamma = -1.0;}
         const sgamma = Math.max(Math.sqrt(1.0-cgamma**2),1.0e-9);

         let ctheta = dx_ij*dx_kj+dy_ij*dy_kj+dz_ij*dz_kj;
         if (ctheta>1.0)  {ctheta =  1.0;}
         if (ctheta<-1.0) {ctheta = -1.0;}
         const stheta = Math.max(Math.sqrt(1.0-ctheta**2),1.0e-9);

         const c2gamma = 2.0*sgamma*sgamma-1.0;

         E += KIJKL*(C0 + C1*sgamma + C2*c2gamma);

         const dE_dW = -KIJKL*(C1*cgamma-4.0*C2*cgamma*sgamma);

         /* t1 = rlj x rkj */
         const t1x = dy_lj*dz_kj - dz_lj*dy_kj;
         const t1y = dz_lj*dx_kj - dx_lj*dz_kj;
         const t1z = dx_lj*dy_kj - dy_lj*dx_kj;

         /* t2 = rij x rlj */
         const t2x = dy_ij*dz_lj - dz_ij*dy_lj;
         const t2y = dz_ij*dx_lj - dx_ij*dz_lj;
         const t2z = dx_ij*dy_lj - dy_ij*dx_lj;

         /* t3 = rkj x rij */
         const t3x = dy_kj*dz_ij - dz_kj*dy_ij;
         const t3y = dz_kj*dx_ij - dx_kj*dz_ij;
         const t3z = dx_kj*dy_ij - dy_kj*dx_ij;
 
         const term1 = sgamma*stheta;
         const term2 = cgamma/(sgamma*stheta*stheta);

         const tg1x = (t1x/term1-(dx_ij-dx_kj*ctheta)*term2)/rij;
         const tg1y = (t1y/term1-(dy_ij-dy_kj*ctheta)*term2)/rij;
         const tg1z = (t1z/term1-(dz_ij-dz_kj*ctheta)*term2)/rij;

         const tg3x = (t2x/term1-(dx_kj-dx_ij*ctheta)*term2)/rkj;
         const tg3y = (t2y/term1-(dy_kj-dy_ij*ctheta)*term2)/rkj;
         const tg3z = (t2z/term1-(dz_kj-dz_ij*ctheta)*term2)/rkj;

         const tg4x = (t3x/term1-dx_lj*cgamma/sgamma)/rlj;
         const tg4y = (t3y/term1-dy_lj*cgamma/sgamma)/rlj;
         const tg4z = (t3z/term1-dz_lj*cgamma/sgamma)/rlj;

         grad[3*i]   += dE_dW*tg1x;
         grad[3*i+1] += dE_dW*tg1y;
         grad[3*i+2] += dE_dW*tg1z;

         grad[3*j]   -= dE_dW*(tg1x+tg3x+tg4x);
         grad[3*j+1] -= dE_dW*(tg1y+tg3y+tg4y);
         grad[3*j+2] -= dE_dW*(tg1z+tg3z+tg4z);

         grad[3*k]   += dE_dW*tg3x;
         grad[3*k+1] += dE_dW*tg3y;
         grad[3*k+2] += dE_dW*tg3z;

         grad[3*l]   += dE_dW*tg4x;
         grad[3*l+1] += dE_dW*tg4y;
         grad[3*l+2] += dE_dW*tg4z;
      }
      return [E,grad];
   }

   /*****************************
    *          LJ               *
    *****************************/
   LJ_e(nion,rion) {
      let E = 0.0;
      for (let i=0; i<(nion-1); ++i) { 
         for (let j=i+1; j<nion; ++j) { 
            const Dij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][0];
            const xij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][1];

            for (let l=0; l<this.nshl3d; ++l) {
               if ((l>0) || ((!this.neighbors1[i].includes(j)) && (!this.neighbors12[i].includes(j)))) {
                  let [dx,dy,dz] = [rion[3*i]  -rion[3*j]  +this.rcell[3*l],
                                    rion[3*i+1]-rion[3*j+1]+this.rcell[3*l+1],
                                    rion[3*i+2]-rion[3*j+2]+this.rcell[3*l+2]];
                  const r = Math.sqrt(dx*dx + dy*dy + dz*dz);
                  let   s = xij/r;
                  if (s>2.1225) {s=2.1225;}
                  const s6  = s**6;
                  const s12 = s6*s6;
                  E += Dij*(-2.0*s6 + s12);
               }
            }
         }
      }
      return E; 
   }

   LJ_egrad(nion,rion) {
      let E = 0.0;
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0;}
      for (let i=0; i<(nion-1); ++i) {
         for (let j=i+1; j<nion; ++j) {
            const Dij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][0];
            const xij = this.preuff[packindx(this.nkatom_type,this.katom[i],this.katom[j])][1];

            for (let l=0; l<this.nshl3d; ++l) {
               if ((l>0) || ((!this.neighbors1[i].includes(j)) && (!this.neighbors12[i].includes(j)))) {
                  let [dx,dy,dz] = [rion[3*i]  -rion[3*j]  +this.rcell[3*l],
                                    rion[3*i+1]-rion[3*j+1]+this.rcell[3*l+1],
                                    rion[3*i+2]-rion[3*j+2]+this.rcell[3*l+2]];
                  const r = Math.sqrt(dx*dx + dy*dy + dz*dz);
                  let s = xij/r;
                  if (s>2.1225) {s=2.1225;}
                  const s6  = s**6;
                  const s12 = s6*s6;
                  const dedr = Dij*(12.0*s6 - 12.0*s12)/r;
                  E += Dij*(-2.0*s6 + s12);
                  grad[3*i]   += dedr*(dx/r);
                  grad[3*i+1] += dedr*(dy/r);
                  grad[3*i+2] += dedr*(dz/r);
                  grad[3*j]   -= dedr*(dx/r);
                  grad[3*j+1] -= dedr*(dy/r);
                  grad[3*j+2] -= dedr*(dz/r);
               }
            }
         }
      }
      return [E,grad];
   }
   

   /*****************************
    *        Combo              *
    *****************************/
   all_e(nion,rion) {
      let E  = this.bondstretch_e(nion,rion);
      E += this.anglebend_e(nion,rion);
      E += this.torsion_e(nion,rion);
      E += this.inversion_e(nion,rion);
      E += this.LJ_e(nion,rion);
      return E;
   }

   all_egrad(nion,rion) {
      const Egrad1 = this.bondstretch_egrad(nion,rion);
      const Egrad2 = this.anglebend_egrad(nion,rion);
      const Egrad3 = this.torsion_egrad(nion,rion);
      const Egrad4 = this.inversion_egrad(nion,rion);
      const Egrad5 = this.LJ_egrad(nion,rion);
      let E = Egrad1[0] + Egrad2[0] + Egrad3[0] + Egrad4[0] + Egrad5[0];
      let grad = new Array(3*nion); 
      for (let i=0; i<(3*nion); ++i) {grad[i] = Egrad1[1][i] + Egrad2[1][i] + Egrad3[1][i] + Egrad4[1][i] + Egrad5[1][i];}
      return [E,grad];
   }

   all_egrad_numerical(nion,rion) {
      let E = this.eall(nion,rion);
      let grad = new Array(3*nion); for (let ii=0; ii<(3*nion); ++ii) {grad[ii] = 0.0;}
      const delta = 0.000001;
      for (let i=0; i<(3*nion); ++i) {
         rion[i] += delta;
         let Ep = this.eall(nion,rion);
         rion[i] -= 2*delta;
         let Em = this.eall(nion,rion)
         rion[i] += delta;
         grad[i] = (Ep-Em)/(2.0*delta);
      }
      return [E,grad]
   }

   /*****************************
    *        Printing           *
    *****************************/
   print_params(){
      const eoln = '\n';
      let astr = eoln;
      astr += sprintf("UFF Bondstretch Potential Parameters\n");
      astr += sprintf("%5s %5s %8s %9s\n","i","j","rij","Kij");
      for (const bs of this.bondstretch) {
         astr += vsprintf("%5d %5d %8.3f %9.3f\n",bs);
      }
      if (this.anglebend.length>0) {
         astr += sprintf("UFF Anglebend Potential Parameters\n");
         astr += sprintf("%5s %5s %5s %5s %9s %8s\n","i","j","k","hybr.","thetaijk","ctheta");
         for (const ab of this.anglebend) {
            astr += vsprintf("%5d %5d %5d %5d %9.3f %8.3f\n",ab);
         }
      }
      if (this.torsion.length>0) {
         astr += sprintf("UFF Torsion Potential Parameters\n");
         astr += sprintf("%5s %5s %5s %5s %8s %5s %8s\n","i","j","k","l","V","n","cnphi");
         for (const tr of this.torsion) {
            astr += vsprintf("%5d %5d %5d %5d %8.3f %5d %8.3f\n",tr);
         }
      }
      if (this.inversion.length>0) {
         astr += sprintf("UFF Inversion Potential Parameters\n");
         astr += sprintf("%5s %5s %5s %5s %8s %8s %8s %8s\n","i","j","k","l","Kijkl","C0","C1","C2");
         for (const iv of this.inversion) {
            astr += vsprintf("%5d %5d %5d %5d %8.3f %8.3f %8.3f %8.3f\n",iv);
         }
      }

      if (this.nkatom_type>0) {
         let katom_type = Array.from(new Set(this.ufftype));
         astr += sprintf("UFF LJ Potential Parameters\n");
         astr += sprintf("%5s %8s %8s\n","atom","x1","D1");
         for (let ia=0; ia<this.nkatom_type; ++ia) {
            let ss = eric_uffparam[katom_type[ia]];
            astr += sprintf("%5s %8.3f %8.3f\n",ss[0],ss[3],ss[4]);
         }
      }

      return astr;
   }

   print_mol(nion,symbol,amatrix,rion) {
      const nbonds = this.bondstretch.length;
      const eoln = '\n';
      let astr = eoln;
      astr += ' EMSLArrows0000000001A' + eoln + eoln;
      astr += sprintf("%3d %2d  0  0  0  0  0  0  0  0999 V2000",nion,nbonds) + eoln;
      for (let i=0; i<nion; ++i) {
         astr += sprintf(" %9.4f %9.4f %9.4f %s",rion[3*i],rion[3*i+1],rion[3*i+2],symbol[i]);
         astr += "  0  0  0  0  0  0  0  0  0  0  0  0" + eoln;
      }
      for (const bs of this.bondstretch) {
         const i   = bs[0];
         const j   = bs[1];
         const aij = amatrix[i+j*nion];
         astr += sprintf("%3d %2d %2d",i+1,j+1,aij);
         astr += "  0  0  0  0" + eoln;
      }
      astr += 'M  END' + eoln;
      astr += '$$$$' + eoln;
      return astr;
   }

   print_xyz(nion,symbol,amatrix,rion) {
      const eoln = '\n';
      let astr = sprintf("%d\n\n",nion);
      for (let i=0; i<nion; ++i) {
         astr += sprintf("%s  %12.6f %12.6f %12.6f\n",symbol[i],rion[3*i],rion[3*i+1],rion[3*i+2]);
      }
      return astr;
   }


}


/*************************************** UFF Potential ********************************************/

/***************************************** xyzsdf2amatrix  ****************************************/

var eric_covalentstr = `
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
Uuo 157  0 0 0`;

var eric_rcovalent = {};
var tmpj = eric_covalentstr.trim().split('\n');
for (let i=0; i<tmpj.length; ++i) {
   let ss = tmpj[i].split(/\s+/);
   eric_rcovalent[ss[0]] = [0.01*eval(ss[1]),0.01*eval(ss[2]),0.01*eval(ss[3]),0.01*eval(ss[4])];
}

/****************************************** 
 *                                        *
 *            eric_bond_order             *
 *                                        *
 ******************************************/
function eric_bond_order(rc1,rc2,r12) {
   const dd = 0.0001;
   const cov = [Math.abs(r12-(rc1[0]+rc2[0]))/(rc1[0]+rc2[0]+dd),
                Math.abs(r12-(rc1[1]+rc2[1]))/(rc1[1]+rc2[1]+dd),
                Math.abs(r12-(rc1[2]+rc2[2]))/(rc1[2]+rc2[2]+dd),
                Math.abs(r12-(rc1[3]+rc2[3]))/(rc1[3]+rc2[3]+dd)];
   let imin = 0;
   let dmin = cov[0];
   if (cov[1]<dmin) {
      dmin = cov[1];
      imin = 1;
   }
   if (cov[2]<dmin) {
      dmin = cov[2];
      imin = 2;
   }
   if (cov[3]<dmin) {
      dmin = cov[3];
      imin = 3;
   }
   b = 0;
   if (cov[imin]<0.10) {
      b = 1+imin;
      if (imin==3) {
         b = 1.5;
      }
   } 

   return b;
}



/****************************************** 
 *                                        *
 *            xyzsdf2amatrix              *
 *                                        *
 ******************************************/

function xyzsdf2amatrix(sdf) {

   var nion,nbond,bonding,amatrix,symbol,rxyz;

   /* parse mol, sdf file */
   if (sdf.includes("V2000")) {
      //var nion  = eval(sdf.split("V2000")[0].split("\n")[-1].split()[0]);
      //var nbond = eval(sdf.split("V2000")[0].split("\n")[-1].split()[1]);
      let tmp  = sdf.split("V2000")[0].split("\n");
      nion  = eval(tmp[tmp.length-1].trim().split(/\s+/)[0]);
      nbond = eval(tmp[tmp.length-1].trim().split(/\s+/)[1]);

      //console.log("nion=",nion," nbond=",nbond);

      //geom = "\n".join(sdf.split("V2000")[1].split("\n")[1:nion+1])
      let geom = sdf.split("V2000")[1].split("\n").slice(1,nion+1).join("\n");
      //console.log("geom=",geom);

      //bonding = "\n".join(sdf.split("V2000")[1].split("\n")[nion+1:nion+1+nbond])
      bonding = sdf.split("V2000")[1].split("\n").slice(nion+1,nion+1+nbond).join("\n");
      //console.log("bonding=",bonding);

      //console.log("NION=",nion);
      amatrix = new Array(nion*nion); 
      for (let ii=0; ii<(nion*nion); ++ii) { amatrix[ii] = 0.0;}
      symbol = [];
      rxyz   = [];

      /* this will change in javascript - currently doesn't handle +4 charge */
      let i = 0;
      for (const aa of geom.split("\n")) {
         let ss = aa.trim().split(/\s+/);
         let qq = eval(ss[5]);
         if (Math.abs(qq)>1.0e-6) {
            qq = 4-qq;
            amatrix[i+i*nion] = qq;
         }
         rxyz.push(eval(ss[0]));
         rxyz.push(eval(ss[1]));
         rxyz.push(eval(ss[2]));
         symbol.push(ss[3]);
         i += 1;
      }

   /* parse xyz file */
   } else {
      nbond = 0;
      nion = eval(sdf.split("\n")[0].trim());
   
      amatrix = new Array(nion*nion); for (let ii=0; ii<(nion*nion); ++ii) amatrix[ii] = 0.0;
      symbol = [];
      rxyz   = [];
      for (const aa of sdf.trim().split("\n").slice(2)) {
         let ss = aa.trim().split(/\s+/);
         symbol.push(ss[0]);
         rxyz.push(eval(ss[1]));
         rxyz.push(eval(ss[2]));
         rxyz.push(eval(ss[3]));
      }
   }
      
   /* build adjacency amatrix from geometry */
   if (nbond==0) {
      for (let i=0; i<nion; ++i) {
         for (let j=0; j<nion; ++j) {
            let symi = symbol[i];
            let symj = symbol[j];
            let rci  = eric_rcovalent[symbol[i]];
            let rcj  = eric_rcovalent[symbol[j]];
            let dx = rxyz[3*i]   - rxyz[3*j];
            let dy = rxyz[3*i+1] - rxyz[3*j+1];
            let dz = rxyz[3*i+2] - rxyz[3*j+2];
            let r = Math.sqrt(dx*dx + dy*dy + dz*dz);
            if (i!=j) {
               let b = eric_bond_order(rci,rcj,r)
               if ((b<1.0) && (symi==symj) && (r<(2.5*rci[0]))) { b = 1; }
               amatrix[i+j*nion] = b;
            }
         }
      }

   /* build amatrix from bonding data */
   } else {
      for (const bb of bonding.split("\n")) {
         let ss = bb.trim().split(/\s+/);
         //console.log("BB,SS=",bb,ss);
         let i = eval(ss[0])-1;
         let j = eval(ss[1])-1;
         let v = eval(ss[2]);
         amatrix[i+j*nion] = v;
         amatrix[j+i*nion] = v;
      }
   }

   return [nion,symbol,rxyz,amatrix];
}




/****************************************** 
 *                                        *
 *            xyza1a2a3amatrix            *
 *                                        *
 ******************************************/

function xyza1a2a3amatrix(sdf,a1,a2,a3) {

   var nion,amatrix,symbol,rxyz;


   /* parse xyz file */
   nion = eval(sdf.split("\n")[0].trim());
   
   amatrix = new Array(nion*nion); for (let ii=0; ii<(nion*nion); ++ii) amatrix[ii] = 0.0;
   symbol = [];
   rxyz   = [];
   for (const aa of sdf.trim().split("\n").slice(2)) {
      let ss = aa.trim().split(/\s+/);
      symbol.push(ss[0]);
      rxyz.push(eval(ss[1]));
      rxyz.push(eval(ss[2]));
      rxyz.push(eval(ss[3]));
   }
      
   /* build adjacency amatrix from geometry */
   for (let i=0; i<nion; ++i) {
      for (let j=0; j<nion; ++j) {
         let symi = symbol[i];
         let symj = symbol[j];
         let rci  = eric_rcovalent[symbol[i]];
         let rcj  = eric_rcovalent[symbol[j]];

         let r = 1.9e9;
         for (let i3=-1; i3<2; ++i3) {
            for (let i2=-1; i2<2; ++i2) {
               for (let i1=-1; i1<2; ++i1) {
                  let dx = rxyz[3*i]   - rxyz[3*j]   + i1*a1[0] + i2*a2[0] + i3*a3[0];
                  let dy = rxyz[3*i+1] - rxyz[3*j+1] + i1*a1[1] + i2*a2[1] + i3*a3[1];
                  let dz = rxyz[3*i+2] - rxyz[3*j+2] + i1*a1[2] + i2*a2[2] + i3*a3[2];
                  let rtmp = Math.sqrt(dx*dx + dy*dy + dz*dz);
                  if (rtmp<r) {
                     r = rtmp;
                  }
               }
            }
         }

         if (i!=j) {
            let b = eric_bond_order(rci,rcj,r)
            if ((b<1.0) && (symi==symj) && (r<(2.5*rci[0]))) { b = 1; }
            amatrix[i+j*nion] = b;
         }
      }
   }


   return [nion,symbol,rxyz,amatrix];
}




var eric_periodic_table_mass = { 'H'  : 1.008, 'He' : 4.0026, 'Li' : 7.016, 'Be' : 9.01218, 'B'  : 11.00931, 'C'  : 12.0, 'N'  : 14.00307, 'O'  : 15.99491, 'F'  : 18.9984, 'Ne' : 19.99244, 'Na' : 22.9898, 'Mg' : 23.98504, 'Al' : 26.98154, 'Si' : 27.97693, 'P'  : 30.97376, 'S'  : 31.97207, 'Cl' : 34.96885, 'Ar' : 39.9624, 'K'  : 38.96371, 'Ca' : 39.96259, 'Sc' : 44.95592, 'Ti' : 45.948, 'V'  : 50.9440, 'Cr' : 51.9405, 'Mn' : 54.9381, 'Fe' : 55.9349, 'Co' : 58.9332, 'Ni' : 57.9353, 'Cu' : 62.9298, 'Zn' : 63.9291, 'Ga' : 68.9257, 'Ge' : 73.9219, 'As' : 74.9216, 'Se' : 78.9183, 'Br' : 79.9165, 'Kr' : 83.912, 'Rb' : 84.9117, 'Sr' : 87.9056, 'Y'  : 88.9054, 'Zr' : 89.9043, 'Nb' : 92.9060, 'Mo' : 97.9055, 'Tc' : 97.9072, 'Ru' : 101.9037, 'Rh' : 102.9048, 'Pd' : 105.9032, 'Ag' : 106.90509, 'Cd' : 113.9036, 'In' : 114.9041, 'Sn' : 117.9018, 'Sb' : 120.9038, 'Te' : 129.9067, 'I'  : 126.9004, 'Xe' : 131.9042, 'Cs' : 132.9051, 'Ba' : 137.9050, 'La' : 138.9061, 'Ce' : 139.9053, 'Pr' : 140.9074, 'Nd' : 143.9099, 'Pm' : 144.9128, 'Sm' : 151.9195, 'Eu' : 152.920, 'Gd' : 157.9241, 'Tb' : 159.9250, 'Dy' : 163.9288, 'Ho' : 164.9303, 'Er' : 165.930, 'Tm' : 168.9344, 'Yb' : 173.9390, 'Lu' : 174.9409, 'Hf' : 179.9468, 'Ta' : 180.948, 'W'  : 183.9510, 'Re' : 186.9560, 'Os' : 189.9586, 'Ir' : 192.9633, 'Pt' : 194.9648, 'Au' : 196.9666, 'Hg' : 201.9706, 'Tl' : 204.9745, 'Pb' : 207.9766, 'Bi' : 208.9804, 'Po' : 209.9829, 'At' : 210.9875, 'Rn' : 222.0175, 'Fr' : 223.0198, 'Ra' : 226.0254, 'Ac' : 227.0278, 'Th' : 232.0382, 'Pa' : 231.0359, 'U'  : 238.0508, 'Np' : 237.0482, 'Pu' : 244.0642, 'Am' : 243.0614, 'Cm' : 247.0704, 'Bk' : 247.0703, 'Cf' : 251.0796, 'Es' : 252.0829, 'Fm' : 257.0950, 'Md' : 258.0986, 'No' : 259.1009, 'Lr' : 262.1100, 'Rf' : 261.1087, 'Ha' : 262.1138, 'Sg' : 266.1219, 'Bh' : 262.1229, 'Hs' : 267.1318, 'Mt' : 268.1388};



/****************************************** 
 *                                        *
 *            xyzsdf_minimize             *
 *                                        *
 ******************************************/
function xyzsdf_minimize(molecule_str,mdparam_str,maxit,time_step,maxerr,ismol,oprint,has_lattice,a1,a2,a3) {

   const eoln = "\n";
   let astr = eoln;
   astr += sprintf("          _____________________________________________________________ ") + eoln; 
   astr += sprintf("          |                                                           | ") + eoln; 
   astr += sprintf("          |                     xyzsdf_minimizer                      | ") + eoln; 
   astr += sprintf("          |                                                           | ") + eoln; 
   astr += sprintf("          |            (Arrows version 1.00 - 4/15/2021)              | ") + eoln; 
   astr += sprintf("          |                                                           | ") + eoln; 
   astr += sprintf("          |      Javascript code to optimize molcules, surfaces,      | ") + eoln; 
   astr += sprintf("          |      and solids using MD potentials. Developed by         | ") + eoln; 
   astr += sprintf("          |      Eric J. Bylaska.                                     | ") + eoln; 
   astr += sprintf("          |___________________________________________________________|\n") + eoln; 
   astr += sprintf("---------------------- Job Started - %s --------------------------\n",new Date().toLocaleString()) + eoln;
   astr += "xyzsdf input:\n" + molecule_str + "\n:xyzsdf_input\n" + eoln;

   let cputime0 = performance.now();
   let [nion,symbols,rion,amatrix] = xyzsdf2amatrix(molecule_str);
   //let [nion,symbols,rion,amatrix] = xyza1a2a3amatrix(molecule_str,a1,a2,a3);

   var mdpotential;
   let bstr = "";
   let mdpotential_type = 0;
   let Ebs = 0.0;
   let Eab = 0.0;
   let Etr = 0.0;
   let Eiv = 0.0;
   let Elj = 0.0;

   /* convert time from au to work with (kcal/mol / ang) forces   */
   let dti = new Array(nion);
   for (let ii=0; ii<(nion); ++ii) {
      dti[ii] = (time_step/(eric_periodic_table_mass[symbols[ii]]*1822.80)) * (0.529177/(27.2116*23.06));
   }

   //set actlist and actlist3
   let symlist =  [];
   if (mdparam_str.includes("frozen")) {
      symlist = mdparam_str.split("frozen")[1].split(";")[0].split(/[ ,]+/);
   }
   let actcount = 0;
   for (let ii=0; ii<(nion); ++ii) {
      if (!symlist.includes(symbols[ii])) {actcount += 1;}
   }
   let actlist  = new Array(actcount);
   let actlist3 = new Array(3*actcount);
   let jj = 0;
   for (let ii=0; ii<(nion); ++ii) {
      if (!symlist.includes(symbols[ii])) {
         actlist[jj]      = ii;
         actlist3[3*jj]   = 3*ii;
         actlist3[3*jj+1] = 3*ii+1;
         actlist3[3*jj+2] = 3*ii+2;
         jj += 1;
      }
   }

   if (mdparam_str.includes("uff")) { console.log("found uff !!!"); mdpotential_type=0; }
   if (mdparam_str.includes("lj-potential-fcc-metals")) { console.log("found lj-potential-fcc-metals !!!"); mdpotential_type=1; }


   /* set the uff potential */
   if (mdpotential_type==0) {
      mdpotential = new UFF_Potential(nion,symbols,amatrix);

   /* set the LJ potential */
   } else if (mdpotential_type==1) {
      mdpotential = new Bylaska_MD(mdparam_str,nion,symbols);
   }

   bstr = mdpotential.print_params() + eoln;

   let cstr = eoln;
   if (has_lattice) { 
      cstr += sprintf("\nlattice vectors:") + eoln;
      cstr += vsprintf("a1 = %12.4f %12.4f %12.4f",a1) + eoln;
      cstr += vsprintf("a2 = %12.4f %12.4f %12.4f",a2) + eoln;
      cstr += vsprintf("a3 = %12.4f %12.4f %12.4f",a3) + eoln;
      mdpotential.mdlat_setter(a1,a2,a3);
   } else {
      cstr += sprintf("\nNo lattice - free-space boundary conditions") + eoln;
   }

   let done = false;
   let it = 1;
   let E = 0.0;
   let Eold = 0.0;
   let Eerr = 0.0;
   let err = 0.0;

   cstr += sprintf("\nTechnical Parameters") + eoln;
   cstr += sprintf("maxiter   = %12d",maxit) + eoln;
   cstr += sprintf("time_step = %12.4f",time_step) + eoln;
   cstr += sprintf("maxerr    = %12.4e",maxerr) + eoln;

   let dstr = sprintf("\n------------------- Iteration Started - %s -----------------------\n",new Date().toLocaleString()) + eoln;
   dstr += sprintf("\n%6s %15s %14s %14s %8s","iter.","E","E-Eold","Error","time_step") + eoln;
   dstr += sprintf("-------------------------------------------------------------") + eoln;

   let cputime1 = performance.now();
   while (!done) {
      let eegrad = mdpotential.all_egrad(nion,rion);
      E        = eegrad[0];
      let grad = eegrad[1];
      err = 0.0;
      for (const i of actlist3) {
         err += grad[i]*grad[i];
      }
      for (const ii of actlist) {
         rion[3*ii]   -= dti[ii]*grad[3*ii];
         rion[3*ii+1] -= dti[ii]*grad[3*ii+1];
         rion[3*ii+2] -= dti[ii]*grad[3*ii+2];
      }

      // Keep in lattice
      //for (const ii of actlist) {
      //   [rion[3*ii],rion[3*ii+1],rion[3*ii+2]] = mdpotential.mdlat_min_diff(rion[3*ii],rion[3*ii+1],rion[3*ii+2]);
      //}

      //for (let i=0; i<(3*nion); ++i) {err += grad[i]*grad[i];}
      //for (let i=0; i<(3*nion); ++i) {rion[i] -= alpha*grad[i];}
      //for (let i=0; i<nion;     ++i) {[rion[3*i],rion[3*i+1],rion[3*i+2]] = mdpotential.mdlat_min_diff(rion[3*i],rion[3*i+1],rion[3*i+2]);}
      err = Math.sqrt(err)/(3*nion);

      dstr += sprintf("%6d %15.9f %14.6e %14.6e %8.2f",it,E,E-Eold,err,time_step) + eoln;
      Eerr = E-Eold;
      Eold = E;
      it +=1;
      done = ((it>maxit) || (err<maxerr));
   }
   if (mdpotential_type==0) {
      Ebs = mdpotential.bondstretch_e(nion,rion);
      Eab = mdpotential.anglebend_e(nion,rion);
      Etr = mdpotential.torsion_e(nion,rion);
      Eiv = mdpotential.inversion_e(nion,rion);
      Elj = mdpotential.LJ_e(nion,rion);
   } else if (mdpotential_type==1) {
      Elj = E
   }
   let cputime2 = performance.now();
   dstr += sprintf("------------------- Iteration Ended - %s -------------------------\n",new Date().toLocaleString()) + eoln;
   


   var molecule_output_str;
   if (ismol) {
      molecule_output_str = mdpotential.print_mol(nion,symbols,amatrix,rion);
   } else {
      molecule_output_str = mdpotential.print_xyz(nion,symbols,amatrix,rion);
   }
   let cputime3 = performance.now();
  
   let estr = "xyzsdf output:\n" + molecule_output_str + "\n:xyzsdf_output\n" + eoln;

   let fstr = sprintf("\nSummary of Energies and Errors\n") + eoln;
   fstr += sprintf("total energy             = %12.6f kcal/mol\n", Ebs+Eab+Etr+Eiv+Elj) + eoln;
   fstr += sprintf(" - Lennard Jones energy  = %12.6f kcal/mol\n", Elj) + eoln;
   if (mdpotential_type==0) {
      fstr += sprintf(" - total repulsion energy= %12.6f kcal/mol\n", Ebs+Eab+Etr+Eiv) + eoln;
      fstr += sprintf("            o bondstretch= %12.6f kcal/mol (%6.2f%s of total repulsion energy)\n", Ebs,100*Ebs/(Ebs+Eab+Etr+Eiv),"%") + eoln;
      fstr += sprintf("            o anglebend  = %12.6f kcal/mol (%6.2f%s of total repulsion energy)\n", Eab,100*Eab/(Ebs+Eab+Etr+Eiv),"%") + eoln;
      fstr += sprintf("            o torsion    = %12.6f kcal/mol (%6.2f%s of total repulsion energy)\n", Etr,100*Etr/(Ebs+Eab+Etr+Eiv),"%") + eoln;
      fstr += sprintf("            o inversion  = %12.6f kcal/mol (%6.2f%s of total repulsion energy)\n", Eiv,100*Eiv/(Ebs+Eab+Etr+Eiv),"%") + eoln;
   }

   fstr += sprintf("\nenergy error    = %12.6e \n", Eerr) + eoln;
   fstr += sprintf("gradient error  = %12.6e \n", err) + eoln;

   fstr += sprintf("\nJob Timings") + eoln;
   fstr += sprintf("prologue    : %10.6e milliseconds", (cputime1 - cputime0)) + eoln;
   fstr += sprintf("main loop   : %10.6e milliseconds", (cputime2 - cputime1)) + eoln;
   fstr += sprintf("epilogue    : %10.6e milliseconds", (cputime3 - cputime2)) + eoln;
   fstr += sprintf("total       : %10.6e milliseconds", (cputime3 - cputime0)) + eoln;
   fstr += sprintf("cputime/step: %10.6e milliseconds/iteration (%d evaluations)", (cputime2 - cputime1)/it,it) + eoln;

   fstr += sprintf("\n---------------------- Job Finished - %s -------------------------\n\n",new Date().toLocaleString()) + eoln;
 
   if (oprint) {
      console.log(astr);
      console.log(bstr);
      console.log(cstr);
      console.log(dstr);
      console.log(estr);
      console.log(fstr);
   }

   return molecule_output_str;
}




/***************************************** xyzsdf2amatrix  ****************************************/


/*

var molecule_str = `
 OpenBabel08131800473D

 12 12  0  0  0  0  0  0  0  0999 V2000
   -0.7616    1.1787   -0.0043 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.6312    1.2536   -0.0069 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.3924    0.0848   -0.0089 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.7609   -1.1588   -0.0083 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.6320   -1.2337   -0.0057 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.3932   -0.0649   -0.0037 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.3547    2.0893   -0.0027 H   0  0  0  0  0  0  0  0  0  0  0  0
    1.1232    2.2225   -0.0073 H   0  0  0  0  0  0  0  0  0  0  0  0
    2.4776    0.1432   -0.0108 H   0  0  0  0  0  0  0  0  0  0  0  0
    1.3540   -2.0694   -0.0099 H   0  0  0  0  0  0  0  0  0  0  0  0
   -1.1240   -2.2026   -0.0053 H   0  0  0  0  0  0  0  0  0  0  0  0
   -2.4784   -0.1233   -0.0018 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0  0  0  0
  1  6  1  0  0  0  0
  1  7  1  0  0  0  0
  2  3  1  0  0  0  0
  2  8  1  0  0  0  0
  3  4  2  0  0  0  0
  3  9  1  0  0  0  0
  4  5  1  0  0  0  0
  4 10  1  0  0  0  0
  5  6  2  0  0  0  0
  5 11  1  0  0  0  0
  6 12  1  0  0  0  0
M  END
$$$$`;

let a1 = [30.0, 0.0, 0.0];
let a2 = [ 0.0,30.0, 0.0];
let a3 = [ 0.0, 0.0,15.0];
var molstrf2 =  xyzsdf_minimize(molecule_str,1200,1.0e-4,1.0e-9,true,true,a1,a2,a3);


*/


