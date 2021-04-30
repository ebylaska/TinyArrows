Clazz.declarePackage ("JS");
Clazz.load (["JU.Lst", "$.V3"], "JS.CIPChirality", ["java.util.Arrays", "$.Hashtable", "JU.BS", "$.Measure", "$.P4", "$.PT", "JU.BSUtil", "$.Logger", "JV.JC"], function () {
c$ = Clazz.decorateAsClass (function () {
this.ptID = 0;
this.root = null;
this.currentRule = 1;
this.lstSmallRings = null;
this.bsAtropisomeric = null;
this.bsKekuleAmbiguous = null;
this.bsAzacyclic = null;
this.vNorm = null;
this.vNorm2 = null;
this.vTemp = null;
if (!Clazz.isClassDefined ("JS.CIPChirality.CIPAtom")) {
JS.CIPChirality.$CIPChirality$CIPAtom$ ();
}
Clazz.instantialize (this, arguments);
}, JS, "CIPChirality");
Clazz.prepareFields (c$, function () {
this.lstSmallRings =  new JU.Lst ();
this.vNorm =  new JU.V3 ();
this.vNorm2 =  new JU.V3 ();
this.vTemp =  new JU.V3 ();
});
Clazz.defineMethod (c$, "getRuleName", 
function () {
return JS.CIPChirality.ruleNames[this.currentRule];
});
Clazz.makeConstructor (c$, 
function () {
});
Clazz.defineMethod (c$, "init", 
 function () {
this.ptID = 0;
this.lstSmallRings.clear ();
this.bsKekuleAmbiguous = null;
this.bsAtropisomeric =  new JU.BS ();
});
Clazz.defineMethod (c$, "getChiralityForAtoms", 
function (atoms, bsAtoms, bsAtropisomeric, bsHelixM, bsHelixP) {
if (bsAtoms.isEmpty ()) return;
this.init ();
this.bsAtropisomeric = (bsAtropisomeric == null ?  new JU.BS () : bsAtropisomeric);
var bs = JU.BSUtil.copy (bsAtoms);
this.lstSmallRings =  new JU.Lst ();
while (!bs.isEmpty ()) this.getSmallRings (atoms[bs.nextSetBit (0)], bs);

this.bsKekuleAmbiguous = this.getKekule (atoms);
this.bsAzacyclic = this.getAzacyclic (atoms, bsAtoms);
var bsToDo = JU.BSUtil.copy (bsAtoms);
var haveAlkenes = this.preFilterAtomList (atoms, bsToDo);
for (var i = bsToDo.nextSetBit (0); i >= 0; i = bsToDo.nextSetBit (i + 1)) {
var a = atoms[i];
a.setCIPChirality (0);
var c = this.getAtomChiralityLimited (a, null, null, 8);
a.setCIPChirality (c == 0 ? 3 : c);
}
if (haveAlkenes) {
var lstEZ =  new JU.Lst ();
for (var i = bsToDo.nextSetBit (0); i >= 0; i = bsToDo.nextSetBit (i + 1)) this.getAtomBondChirality (atoms[i], lstEZ, bsToDo);

if (this.lstSmallRings.size () > 0 && lstEZ.size () > 0) this.clearSmallRingEZ (atoms, lstEZ);
if (bsHelixM != null) for (var i = bsHelixM.nextSetBit (0); i >= 0; i = bsHelixM.nextSetBit (i + 1)) atoms[i].setCIPChirality (33);

if (bsHelixP != null) for (var i = bsHelixP.nextSetBit (0); i >= 0; i = bsHelixP.nextSetBit (i + 1)) atoms[i].setCIPChirality (34);

}if (JU.Logger.debugging) {
JU.Logger.info ("sp2-aromatic = " + this.bsKekuleAmbiguous);
JU.Logger.info ("smallRings = " + JU.PT.toJSON (null, this.lstSmallRings));
}}, "~A,JU.BS,JU.BS,JU.BS,JU.BS");
Clazz.defineMethod (c$, "getAzacyclic", 
 function (atoms, bsAtoms) {
var bsAza = null;
for (var i = bsAtoms.nextSetBit (0); i >= 0; i = bsAtoms.nextSetBit (i + 1)) {
var atom = atoms[i];
if (atom.getElementNumber () != 7 || atom.getCovalentBondCount () != 3 || this.bsKekuleAmbiguous.get (i)) continue;
var nRings =  new JU.Lst ();
for (var j = this.lstSmallRings.size (); --j >= 0; ) {
var bsRing = this.lstSmallRings.get (j);
if (bsRing.get (i)) nRings.addLast (bsRing);
}
var nr = nRings.size ();
if (nr < 2) continue;
var bsSubs =  new JU.BS ();
var bonds = atom.getEdges ();
for (var b = bonds.length; --b >= 0; ) if (bonds[b].isCovalent ()) bsSubs.set (bonds[b].getOtherAtomNode (atom).getIndex ());

var bsBoth =  new JU.BS ();
var bsAll =  new JU.BS ();
for (var j = 0; j < nr - 1 && bsAll != null; j++) {
var bs1 = nRings.get (j);
for (var k = j + 1; k < nr && bsAll != null; k++) {
var bs2 = nRings.get (k);
JU.BSUtil.copy2 (bs1, bsBoth);
bsBoth.and (bs2);
if (bsBoth.cardinality () > 2) {
JU.BSUtil.copy2 (bs1, bsAll);
bsAll.or (bs2);
bsAll.and (bsSubs);
if (bsAll.cardinality () == 3) {
if (bsAza == null) bsAza =  new JU.BS ();
bsAza.set (i);
bsAll = null;
}}}
}
}
return bsAza;
}, "~A,JU.BS");
Clazz.defineMethod (c$, "preFilterAtomList", 
 function (atoms, bsToDo) {
var haveAlkenes = false;
for (var i = bsToDo.nextSetBit (0); i >= 0; i = bsToDo.nextSetBit (i + 1)) {
if (!this.couldBeChiralAtom (atoms[i])) {
bsToDo.clear (i);
continue;
}if (!haveAlkenes && this.couldBeChiralAlkene (atoms[i], null) != -1) haveAlkenes = true;
}
return haveAlkenes;
}, "~A,JU.BS");
Clazz.defineMethod (c$, "couldBeChiralAtom", 
 function (a) {
var mustBePlanar = false;
switch (a.getCovalentBondCount ()) {
default:
System.out.println ("???? too many bonds! " + a);
return false;
case 0:
return false;
case 1:
return false;
case 2:
return a.getElementNumber () == 7;
case 3:
switch (a.getElementNumber ()) {
case 7:
if (this.bsAzacyclic != null && this.bsAzacyclic.get (a.getIndex ())) break;
return false;
case 6:
mustBePlanar = true;
break;
case 15:
case 16:
case 33:
case 34:
case 51:
case 52:
case 83:
case 84:
break;
case 4:
break;
default:
return false;
}
break;
case 4:
break;
}
var edges = a.getEdges ();
var nH = 0;
for (var j = edges.length; --j >= 0; ) {
if (edges[j].getOtherAtomNode (a).getAtomicAndIsotopeNumber () == 1 && ++nH == 2) {
return false;
}}
var d = this.getTrigonality (a, this.vNorm);
var planar = (Math.abs (d) < 0.2);
if (planar == mustBePlanar) return true;
System.out.println ("??????? planar=" + planar + "??" + a);
return false;
}, "JU.Node");
Clazz.defineMethod (c$, "couldBeChiralAlkene", 
 function (a, b) {
switch (a.getCovalentBondCount ()) {
default:
return -1;
case 2:
if (a.getElementNumber () != 7) return -1;
break;
case 3:
if (!this.isFirstRow (a)) return -1;
break;
}
var bonds = a.getEdges ();
var n = 0;
for (var i = bonds.length; --i >= 0; ) if (bonds[i].getCovalentOrder () == 2) {
if (++n > 1) return -3;
var other = bonds[i].getOtherAtomNode (a);
if (!this.isFirstRow (other)) return -1;
if (b != null && (other !== b || b.getCovalentBondCount () == 1)) {
return -1;
}}
return -2;
}, "JU.Node,JU.Node");
Clazz.defineMethod (c$, "isFirstRow", 
function (a) {
var n = a.getElementNumber ();
return (n > 2 && n <= 10);
}, "JU.Node");
Clazz.defineMethod (c$, "getKekule", 
 function (atoms) {
var bs =  new JU.BS ();
var nRings = this.lstSmallRings.size ();
var bsDone =  new JU.BS ();
for (var i = nRings; --i >= 0; ) {
if (bsDone.get (i)) continue;
var bsRing = this.lstSmallRings.get (i);
if (bsRing.cardinality () != 6) {
bsDone.set (i);
continue;
}var nPI = 0;
for (var j = bsRing.nextSetBit (0); j >= 0; j = bsRing.nextSetBit (j + 1)) {
var a = atoms[j];
if (bs.get (a.getIndex ())) {
nPI++;
continue;
}var nb = a.getCovalentBondCount ();
if (nb == 3 || nb == 2) {
var bonds = a.getEdges ();
for (var k = bonds.length; --k >= 0; ) {
var b = bonds[k];
if (b.getCovalentOrder () != 2) continue;
if (bsRing.get (b.getOtherAtomNode (a).getIndex ())) {
nPI++;
break;
}}
}}
if (nPI == 6) {
bs.or (bsRing);
bsDone.set (i);
i = nRings;
}}
return bs;
}, "~A");
Clazz.defineMethod (c$, "getSmallRings", 
 function (atom, bs) {
this.root = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (atom, null, false, false);
this.addSmallRings (this.root, bs);
}, "JU.Node,JU.BS");
Clazz.defineMethod (c$, "addSmallRings", 
 function (a, bs) {
if (a == null || a.atom == null || a.sphere > 7) return;
if (bs != null) bs.clear (a.atom.getIndex ());
if (a.isTerminal || a.isDuplicate || a.atom.getCovalentBondCount () > 4) return;
var atom2;
var pt = 0;
var bonds = a.atom.getEdges ();
for (var i = bonds.length; --i >= 0; ) {
var bond = bonds[i];
if (!bond.isCovalent () || (atom2 = bond.getOtherAtomNode (a.atom)).getCovalentBondCount () == 1 || a.parent != null && atom2 === a.parent.atom) continue;
var r = a.addAtom (pt++, atom2, false, false);
if (r.isDuplicate) r.updateRingList ();
}
for (var i = 0; i < pt; i++) {
this.addSmallRings (a.atoms[i], bs);
}
}, "JS.CIPChirality.CIPAtom,JU.BS");
Clazz.defineMethod (c$, "clearSmallRingEZ", 
 function (atoms, lstEZ) {
for (var j = this.lstSmallRings.size (); --j >= 0; ) this.lstSmallRings.get (j).andNot (this.bsAtropisomeric);

for (var i = lstEZ.size (); --i >= 0; ) {
var ab = lstEZ.get (i);
for (var j = this.lstSmallRings.size (); --j >= 0; ) {
var ring = this.lstSmallRings.get (j);
if (ring.get (ab[0]) && ring.get (ab[1])) {
atoms[ab[0]].setCIPChirality (3);
atoms[ab[1]].setCIPChirality (3);
}}
}
}, "~A,JU.Lst");
Clazz.defineMethod (c$, "getTrigonality", 
function (a, vNorm) {
var pts =  new Array (3);
var bonds = a.getEdges ();
for (var i = bonds.length, pt = 0; --i >= 0 && pt < 3; ) if (bonds[i].isCovalent ()) pts[pt++] = bonds[i].getOtherAtomNode (a).getXYZ ();

var plane = JU.Measure.getPlaneThroughPoints (pts[0], pts[1], pts[2], vNorm, this.vTemp,  new JU.P4 ());
return JU.Measure.distanceToPlane (plane, a.getXYZ ());
}, "JU.Node,JU.V3");
Clazz.defineMethod (c$, "getAtomChirality", 
function (atom) {
this.init ();
var rs = this.getAtomChiralityLimited (atom, null, null, 8);
return (rs == 0 ? 3 : rs);
}, "JU.Node");
Clazz.defineMethod (c$, "getBondChirality", 
function (bond) {
if (bond.getCovalentOrder () != 2) return 0;
this.init ();
this.lstSmallRings =  new JU.Lst ();
this.getSmallRings (bond.getOtherAtomNode (null), null);
return this.getBondChiralityLimited (bond, null, 8);
}, "JU.Edge");
Clazz.defineMethod (c$, "getAtomBondChirality", 
 function (atom, lstEZ, bsToDo) {
var index = atom.getIndex ();
var bonds = atom.getEdges ();
var c = 0;
var isAtropic = this.bsAtropisomeric.get (index);
for (var j = bonds.length; --j >= 0; ) {
var bond = bonds[j];
var atom1;
var index1;
if (isAtropic) {
atom1 = bonds[j].getOtherAtomNode (atom);
index1 = atom1.getIndex ();
if (!this.bsAtropisomeric.get (index1)) continue;
c = this.getAxialOrEZChirality (atom, atom1, atom, atom1, true, 8);
} else if (bond.getCovalentOrder () == 2) {
atom1 = this.getLastCumuleneAtom (bond, atom, null, null);
index1 = atom1.getIndex ();
if (index1 < index) continue;
c = this.getBondChiralityLimited (bond, atom, 8);
} else {
continue;
}if (c != 0) {
if (!isAtropic) lstEZ.addLast ( Clazz.newIntArray (-1, [index, index1]));
bsToDo.clear (index);
bsToDo.clear (index1);
}if (isAtropic) break;
}
}, "JU.Node,JU.Lst,JU.BS");
Clazz.defineMethod (c$, "getLastCumuleneAtom", 
 function (bond, atom, nSP2, parents) {
var atom2 = bond.getOtherAtomNode (atom);
if (parents != null) {
parents[0] = atom2;
parents[1] = atom;
}if (nSP2 != null) nSP2[0] = 2;
var ppt = 0;
while (true) {
if (atom2.getCovalentBondCount () != 2) return atom2;
var edges = atom2.getEdges ();
for (var i = edges.length; --i >= 0; ) {
var atom3 = (bond = edges[i]).getOtherAtomNode (atom2);
if (atom3 === atom) continue;
if (bond.getCovalentOrder () != 2) return atom2;
if (parents != null) {
if (ppt == 0) {
parents[0] = atom2;
ppt = 1;
}parents[1] = atom2;
}if (nSP2 != null) nSP2[0]++;
atom = atom2;
atom2 = atom3;
break;
}
}
}, "JU.Edge,JU.Node,~A,~A");
Clazz.defineMethod (c$, "getAtomChiralityLimited", 
 function (atom, cipAtom, parent, ruleMax) {
var rs = 0;
var isChiral = false;
var isAlkene = false;
try {
if (cipAtom == null) {
cipAtom = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (atom, null, false, isAlkene);
var nSubs = atom.getCovalentBondCount ();
var elemNo = atom.getElementNumber ();
isAlkene = (nSubs == 3 && elemNo <= 10 && !cipAtom.isTrigonalPyramidal);
if (nSubs != (parent == null ? 4 : 3) - (nSubs == 3 && !isAlkene ? 1 : 0)) return rs;
} else {
atom = cipAtom.atom;
isAlkene = cipAtom.isAlkene;
}this.root = cipAtom;
cipAtom.parent = parent;
if (parent != null) cipAtom.htPathPoints = parent.htPathPoints;
this.currentRule = 1;
if (cipAtom.set ()) {
for (this.currentRule = 1; this.currentRule <= ruleMax; this.currentRule++) {
if (JU.Logger.debugging) JU.Logger.info ("-Rule " + this.getRuleName () + " CIPChirality for " + cipAtom + "-----");
if (this.currentRule == 5) cipAtom.createAuxiliaryRule4Data (null, null);
isChiral = false;
cipAtom.sortSubstituents ();
isChiral = true;
if (JU.Logger.debugging) {
JU.Logger.info (this.currentRule + ">>>>" + cipAtom);
for (var i = 0; i < cipAtom.bondCount; i++) {
if (cipAtom.atoms[i] != null) JU.Logger.info (cipAtom.atoms[i] + " " + Integer.toHexString (cipAtom.priorities[i]));
}
}if (cipAtom.achiral) {
isChiral = false;
break;
}for (var i = 0; i < cipAtom.bondCount - 1; i++) {
if (cipAtom.priorities[i] == cipAtom.priorities[i + 1]) {
isChiral = false;
break;
}}
if (this.currentRule == 8) cipAtom.isPseudo = cipAtom.canBePseudo;
if (isChiral) {
rs = (!isAlkene ? cipAtom.checkHandedness () : cipAtom.atoms[0].isDuplicate ? 2 : 1);
if (!isAlkene && cipAtom.isPseudo && cipAtom.canBePseudo) rs = rs | 4;
if (JU.Logger.debugging) JU.Logger.info (atom + " " + JV.JC.getCIPChiralityName (rs) + " by Rule " + this.getRuleName () + "\n----------------------------------");
break;
}}
}} catch (e) {
System.out.println (e + " in CIPChirality");
{
alert(e);
}return 3;
}
return rs;
}, "JU.Node,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,~N");
Clazz.defineMethod (c$, "getBondChiralityLimited", 
 function (bond, a, ruleMax) {
if (JU.Logger.debugging) JU.Logger.info ("get Bond Chirality " + bond);
if (a == null) a = bond.getOtherAtomNode (null);
var b = bond.getOtherAtomNode (a);
if (this.couldBeChiralAlkene (a, b) == -1) return 0;
var nSP2 =  Clazz.newIntArray (1, 0);
var parents =  new Array (2);
b = this.getLastCumuleneAtom (bond, a, nSP2, parents);
var isCumulene = (nSP2[0] > 2);
var isAxial = isCumulene && (nSP2[0] % 2 == 1);
return this.getAxialOrEZChirality (a, parents[0], parents[1], b, isAxial, ruleMax);
}, "JU.Edge,JU.Node,~N");
Clazz.defineMethod (c$, "getAxialOrEZChirality", 
 function (a, pa, pb, b, isAxial, ruleMax) {
var a1 = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (a, null, false, true);
var atop = this.getAlkeneEndTopPriority (a1, pa, isAxial, ruleMax);
var b2 = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (b, null, false, true);
var btop = this.getAlkeneEndTopPriority (b2, pb, isAxial, ruleMax);
var c = (atop >= 0 && btop >= 0 ? this.getEneChirality (b2.atoms[btop], b2, a1, a1.atoms[atop], isAxial, true) : 0);
if (c != 0 && (isAxial || !this.bsAtropisomeric.get (a.getIndex ()) && !this.bsAtropisomeric.get (b.getIndex ()))) {
a.setCIPChirality (c);
b.setCIPChirality (c);
if (JU.Logger.debugging) JU.Logger.info (a + "-" + b + " " + JV.JC.getCIPChiralityName (c));
}return c;
}, "JU.Node,JU.Node,JU.Node,JU.Node,~B,~N");
Clazz.defineMethod (c$, "getEneChirality", 
function (top1, end1, end2, top2, isAxial, allowPseudo) {
return (top1 == null || top2 == null || top1.atom == null || top2.atom == null ? 0 : isAxial ? (this.isPos (top1, end1, end2, top2) ? 34 : 33) | (allowPseudo && (end2.ties == null) != (end1.ties == null) ? 4 : 0) : (this.isCis (top1, end1, end2, top2) ? 8 : 16));
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,~B,~B");
Clazz.defineMethod (c$, "getAlkeneEndTopPriority", 
 function (a1, pa, isAxial, ruleMax) {
a1.canBePseudo = a1.isOddCumulene = isAxial;
return this.getAtomChiralityLimited (a1.atom, a1, Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (pa, null, false, true), ruleMax) - 1;
}, "JS.CIPChirality.CIPAtom,JU.Node,~B,~N");
Clazz.defineMethod (c$, "isCis", 
function (a, b, c, d) {
JU.Measure.getNormalThroughPoints (a.atom.getXYZ (), b.atom.getXYZ (), c.atom.getXYZ (), this.vNorm, this.vTemp);
var vNorm2 =  new JU.V3 ();
JU.Measure.getNormalThroughPoints (b.atom.getXYZ (), c.atom.getXYZ (), d.atom.getXYZ (), vNorm2, this.vTemp);
return (this.vNorm.dot (vNorm2) > 0);
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "isPos", 
function (a, b, c, d) {
var angle = JU.Measure.computeTorsion (a.atom.getXYZ (), b.atom.getXYZ (), c.atom.getXYZ (), d.atom.getXYZ (), true);
return (angle > 0);
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom");
c$.$CIPChirality$CIPAtom$ = function () {
Clazz.pu$h(self.c$);
c$ = Clazz.decorateAsClass (function () {
Clazz.prepareCallback (this, arguments);
this.atom = null;
this.id = 0;
this.parent = null;
this.rootSubstituent = null;
this.elemNo = 0;
this.massNo = 0;
this.sphere = 0;
this.bsPath = null;
this.myPath = "";
this.rootDistance = 0;
this.nAtoms = 0;
this.nPriorities = 0;
this.h1Count = 0;
this.auxChirality = "~";
this.isSet = false;
this.isDuplicate = true;
this.isTerminal = false;
this.isAlkene = false;
this.alkeneParent = null;
this.alkeneChild = null;
this.isAlkeneAtom2 = false;
this.doCheckPseudo = false;
this.isPseudo = false;
this.achiral = false;
this.bondCount = 0;
this.atoms = null;
this.priorities = null;
this.rule4List = null;
this.atomIndex = 0;
this.auxEZ = -1;
this.canBePseudo = true;
this.ties = null;
this.isOddCumulene = false;
this.nextSP2 = null;
this.nextChiralBranch = null;
this.rule4Count = null;
this.priority = 0;
this.htPathPoints = null;
this.isTrigonalPyramidal = false;
this.isKekuleAmbiguous = false;
this.sp2Duplicate = false;
Clazz.instantialize (this, arguments);
}, JS.CIPChirality, "CIPAtom", null, [Comparable, Cloneable]);
Clazz.prepareFields (c$, function () {
this.atoms =  new Array (4);
this.priorities =  Clazz.newIntArray (4, 0);
});
Clazz.makeConstructor (c$, 
function () {
});
Clazz.defineMethod (c$, "create", 
function (a, b, c, d) {
this.id = ++this.b$["JS.CIPChirality"].ptID;
this.parent = b;
if (a == null) return this;
this.isAlkene = d;
this.atom = a;
this.atomIndex = a.getIndex ();
this.isKekuleAmbiguous = (this.b$["JS.CIPChirality"].bsKekuleAmbiguous != null && this.b$["JS.CIPChirality"].bsKekuleAmbiguous.get (this.atomIndex));
this.elemNo = (c && this.isKekuleAmbiguous ? b.getKekuleElementNumber () : a.getElementNumber ());
this.massNo = a.getNominalMass ();
this.bondCount = a.getCovalentBondCount ();
this.isTrigonalPyramidal = (this.bondCount == 3 && !d && (this.elemNo > 10 || this.b$["JS.CIPChirality"].bsAzacyclic != null && this.b$["JS.CIPChirality"].bsAzacyclic.get (this.atomIndex)));
this.canBePseudo = (this.bondCount == 4 || this.isTrigonalPyramidal);
if (b != null) this.sphere = b.sphere + 1;
if (this.sphere == 1) {
this.rootSubstituent = this;
this.htPathPoints =  new java.util.Hashtable ();
} else if (b != null) {
this.rootSubstituent = b.rootSubstituent;
this.htPathPoints = this.rootSubstituent.htPathPoints;
}this.bsPath = (b == null ?  new JU.BS () : JU.BSUtil.copy (b.bsPath));
this.sp2Duplicate = c;
this.rootDistance = this.sphere;
if (b == null) {
this.bsPath.set (this.atomIndex);
} else if (this.sp2Duplicate && this.isKekuleAmbiguous) {
} else if (a === this.b$["JS.CIPChirality"].root.atom) {
c = true;
this.rootDistance = 0;
} else if (this.bsPath.get (this.atomIndex)) {
c = true;
this.rootDistance = this.rootSubstituent.htPathPoints.get (Integer.$valueOf (this.atomIndex)).intValue ();
} else {
this.bsPath.set (this.atomIndex);
this.rootSubstituent.htPathPoints.put (Integer.$valueOf (this.atomIndex), Integer.$valueOf (this.rootDistance));
}this.isDuplicate = c;
if (JU.Logger.debugging) {
if (this.sphere < 50) this.myPath = (b != null ? b.myPath + "-" : "") + this;
JU.Logger.info ("new CIPAtom " + this.myPath);
}return this;
}, "JU.Node,JS.CIPChirality.CIPAtom,~B,~B");
Clazz.defineMethod (c$, "getKekuleElementNumber", 
 function () {
var a = this.atom.getEdges ();
var b;
var c = 0;
var d = 0;
for (var e = a.length; --e >= 0; ) if ((b = a[e]).isCovalent ()) {
var f = b.getOtherAtomNode (this.atom);
if (this.b$["JS.CIPChirality"].bsKekuleAmbiguous.get (f.getIndex ())) {
d++;
c += f.getElementNumber ();
}}
return c / d;
});
Clazz.defineMethod (c$, "updateRingList", 
function () {
var a = JU.BSUtil.newAndSetBit (this.atomIndex);
var b = this;
var c = -1;
while ((b = b.parent) != null && c != this.atomIndex) a.set (c = b.atomIndex);

if (a.cardinality () <= 7) {
for (var d = this.b$["JS.CIPChirality"].lstSmallRings.size (); --d >= 0; ) if (this.b$["JS.CIPChirality"].lstSmallRings.get (d).equals (a)) return;

this.b$["JS.CIPChirality"].lstSmallRings.addLast (a);
}});
Clazz.defineMethod (c$, "set", 
function () {
if (this.isSet) return true;
this.isSet = true;
if (this.isDuplicate) return true;
var a = this.atom.getEdges ();
var b = a.length;
if (JU.Logger.debuggingHigh) JU.Logger.info ("set " + this);
var c = 0;
for (var d = 0; d < b; d++) {
var e = a[d];
if (!e.isCovalent ()) continue;
var f = e.getOtherAtomNode (this.atom);
var g = (this.parent != null && this.parent.atom === f);
var h = e.getCovalentOrder ();
if (h == 2) {
if (this.elemNo > 10 || !this.b$["JS.CIPChirality"].isFirstRow (f)) h = 1;
 else {
this.isAlkene = true;
if (g) {
this.auxChirality = e.getCIPChirality (false);
if (this.auxChirality.equals ("")) this.auxChirality = "~";
if (this.atom.getCovalentBondCount () == 2 && this.atom.getValence () == 4) {
this.parent.isAlkeneAtom2 = false;
this.parent.auxChirality = "~";
} else {
this.isAlkeneAtom2 = true;
}this.parent.alkeneChild = null;
this.alkeneParent = (this.parent.alkeneParent == null ? this.parent : this.parent.alkeneParent);
this.alkeneParent.alkeneChild = this;
this.alkeneParent.auxChirality = this.auxChirality;
if (this.parent.alkeneParent == null) this.parent.nextSP2 = this;
}}}if (b == 1 && h == 1 && g) {
this.isTerminal = true;
return true;
}switch (h) {
case 3:
if (this.addAtom (c++, f, g, false) == null) {
this.isTerminal = true;
return false;
}case 2:
if (this.addAtom (c++, f, h != 2 || g, h == 2) == null) {
this.isTerminal = true;
return false;
}case 1:
if (!g && this.addAtom (c++, f, h != 1 && this.elemNo <= 10, false) == null) {
this.isTerminal = true;
return false;
}break;
default:
this.isTerminal = true;
return false;
}
}
this.isTerminal = (c == 0);
this.nAtoms = c;
for (; c < this.atoms.length; c++) this.atoms[c] = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (null, this, true, false);

java.util.Arrays.sort (this.atoms);
return true;
});
Clazz.defineMethod (c$, "addAtom", 
function (a, b, c, d) {
if (a >= this.atoms.length) {
if (JU.Logger.debugging) JU.Logger.info (" too many bonds on " + this.atom);
return null;
}if (this.parent == null) {
var e = b.getAtomicAndIsotopeNumber ();
if (e == 1) {
if (++this.h1Count > 1) {
if (JU.Logger.debuggingHigh) JU.Logger.info (" second H atom found on " + this.atom);
return null;
}}}return this.atoms[a] = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (b, this, c, d);
}, "~N,JU.Node,~B,~B");
Clazz.defineMethod (c$, "sortSubstituents", 
function () {
var a =  Clazz.newIntArray (4, 0);
var b =  Clazz.newIntArray (4, 0);
this.ties = null;
for (var c = 0; c < 4; c++) {
b[c] = this.priorities[c];
this.priorities[c] = 0;
}
if (JU.Logger.debugging) {
JU.Logger.info (this.b$["JS.CIPChirality"].root + "---sortSubstituents---" + this);
for (var d = 0; d < 4; d++) {
JU.Logger.info (this.b$["JS.CIPChirality"].getRuleName () + ": " + this + "[" + d + "]=" + this.atoms[d].myPath + " " + Integer.toHexString (b[d]));
}
JU.Logger.info ("---");
}var d = (this.rule4List != null && this.b$["JS.CIPChirality"].currentRule > 5);
for (var e = 0; e < 4; e++) {
var f = this.atoms[e];
for (var g = e + 1; g < 4; g++) {
var h = this.atoms[g];
var i = JU.Logger.debuggingHigh && h.isHeavy () && f.isHeavy ();
var j = (f.atom == null ? 1 : h.atom == null ? -1 : b[e] == b[g] ? 0 : b[g] < b[e] ? 1 : -1);
if (j == 0) j = (d ? this.checkRule4And5 (e, g) : f.checkPriority (h));
if (i) JU.Logger.info (this.dots () + "ordering " + this.id + "." + e + "." + g + " " + this + "-" + f + " vs " + h + " = " + j);
switch (j) {
case -2147483648:
if (d && this.sphere == 0) this.achiral = true;
a[e]++;
if (i) JU.Logger.info (this.dots () + this.atom + "." + h + " ends up with tie with " + f);
break;
case 1:
a[e]++;
this.priorities[e]++;
if (i) JU.Logger.info (this.dots () + this + "." + h + " B-beats " + f);
break;
case -1:
a[g]++;
this.priorities[g]++;
if (i) JU.Logger.info (this.dots () + this + "." + f + " A-beats " + h);
break;
case 0:
switch (this.sign (j = f.breakTie (h))) {
case 0:
a[g]++;
if (i) JU.Logger.info (this.dots () + this + "." + h + " ends up with tie with " + f);
break;
case 1:
a[e]++;
this.priorities[e]++;
if (i) JU.Logger.info (this.dots () + this + "." + h + " wins in tie with " + f);
break;
case -1:
a[g]++;
this.priorities[g]++;
if (i) JU.Logger.info (this.dots () + this + "." + f + " wins in tie with " + h);
break;
}
break;
}
if (this.doCheckPseudo) {
this.doCheckPseudo = false;
if (this.ties == null) this.ties =  new JU.Lst ();
this.ties.addLast ( Clazz.newIntArray (-1, [e, g]));
}}
}
var f =  new Array (4);
var g =  Clazz.newIntArray (4, 0);
var h =  new JU.BS ();
for (var i = 0; i < 4; i++) {
var j = a[i];
var k = f[j] = this.atoms[i];
g[j] = this.priorities[i];
if (k.atom != null) h.set (this.priorities[i]);
}
this.atoms = f;
this.priorities = g;
this.nPriorities = h.cardinality ();
if (this.ties != null && !this.isOddCumulene) {
switch (this.ties.size ()) {
case 1:
switch (this.checkPseudoHandedness (this.ties.get (0), a)) {
case 1:
case 2:
this.isPseudo = this.canBePseudo;
break;
}
break;
case 2:
this.canBePseudo = false;
break;
}
}if (JU.Logger.debugging) {
JU.Logger.info (this.dots () + this.atom + " nPriorities = " + this.nPriorities);
for (var j = 0; j < 4; j++) {
JU.Logger.info (this.dots () + this.myPath + "[" + j + "]=" + this.atoms[j] + " " + this.priorities[j] + " " + Integer.toHexString (this.priorities[j]) + " new");
}
JU.Logger.info (this.dots () + "-------");
}});
Clazz.defineMethod (c$, "dots", 
 function () {
return ".....................".substring (0, Math.min (20, this.sphere));
});
Clazz.defineMethod (c$, "breakTie", 
 function (a) {
if (JU.Logger.debugging && this.isHeavy () && a.isHeavy ()) JU.Logger.info (this.dots () + "tie for " + this + " and " + a + " at sphere " + this.sphere);
if (this.isDuplicate && a.isDuplicate && this.atom === a.atom && this.rootDistance == a.rootDistance) return 0;
var b = this.checkIsDuplicate (a);
if (b != 0) return b * (this.sphere + 1);
if (!this.set () || !a.set () || this.isTerminal && a.isTerminal || this.isDuplicate && a.isDuplicate) return 0;
if (this.isTerminal != a.isTerminal) return (this.isTerminal ? 1 : -1) * (this.sphere + 1);
if (this.b$["JS.CIPChirality"].currentRule == 2) {
this.preSortRule1b ();
a.preSortRule1b ();
}if ((b = this.compareShallowly (a)) != 0) return b;
this.sortSubstituents ();
a.sortSubstituents ();
return this.compareDeeply (a);
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "preSortRule1b", 
 function () {
var a;
var b;
for (var c = 0; c < 3; c++) {
if (!(a = this.atoms[c]).isDuplicate) continue;
for (var d = c + 1; d < 4; d++) {
if (!(b = this.atoms[d]).isDuplicate || a.elemNo != b.elemNo || a.rootDistance <= b.rootDistance) continue;
this.atoms[c] = b;
this.atoms[d] = a;
d = 4;
c = -1;
}
}
});
Clazz.defineMethod (c$, "isHeavy", 
 function () {
return this.massNo > 1;
});
Clazz.defineMethod (c$, "compareShallowly", 
 function (a) {
for (var b = 0; b < this.nAtoms; b++) {
var c = this.atoms[b];
var d = a.atoms[b];
var e = c.checkCurrentRule (d);
if (e == -2147483648) e = 0;
if (e != 0) {
if (JU.Logger.debugging && c.isHeavy () && d.isHeavy ()) JU.Logger.info (c.dots () + "compareShallow " + c + " " + d + ": " + e * c.sphere);
return e * c.sphere;
}}
return 0;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "compareDeeply", 
 function (a) {
var b = (this.nAtoms == 0 ? 1 : 0);
var c = 2147483647;
for (var d = 0; d < this.nAtoms; d++) {
var e = this.atoms[d];
var f = a.atoms[d];
if (JU.Logger.debugging && e.isHeavy () && f.isHeavy ()) JU.Logger.info (e.dots () + "compareDeep sub " + e + " " + f);
var g = e.breakTie (f);
if (g == 0) continue;
var h = Math.abs (g);
if (JU.Logger.debugging && e.isHeavy () && f.isHeavy ()) JU.Logger.info (e.dots () + "compareDeep sub " + e + " " + f + ": " + g);
if (h < c) {
c = h;
b = g;
}}
if (JU.Logger.debugging) JU.Logger.info (this.dots () + "compareDeep " + this + " " + a + ": " + b);
return b;
}, "JS.CIPChirality.CIPAtom");
Clazz.overrideMethod (c$, "compareTo", 
function (a) {
var b;
return (a == null ? -1 : (this.atom == null) != (a.atom == null) ? (this.atom == null ? 1 : -1) : (b = this.checkRule1a (a)) != 0 ? b : this.checkIsDuplicate (a));
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkPriority", 
function (a) {
var b;
return (a == null ? -1 : (this.atom == null) != (a.atom == null) ? (this.atom == null ? 1 : -1) : (b = this.checkCurrentRule (a)) == -2147483648 ? 0 : b);
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkIsDuplicate", 
 function (a) {
return a.isDuplicate == this.isDuplicate ? 0 : a.isDuplicate ? -1 : 1;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkCurrentRule", 
function (a) {
switch (this.b$["JS.CIPChirality"].currentRule) {
default:
case 1:
return this.checkRule1a (a);
case 2:
return this.checkRule1b (a);
case 3:
return this.checkRule2 (a);
case 4:
return this.checkRule3 (a);
case 5:
return this.checkRules4a (a, " sr SR PM");
case 6:
case 7:
case 8:
return 0;
}
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkRule1a", 
 function (a) {
return a.atom == null ? -1 : this.atom == null ? 1 : a.elemNo < this.elemNo ? -1 : a.elemNo > this.elemNo ? 1 : 0;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkRule1b", 
 function (a) {
return a.isDuplicate != this.isDuplicate ? 0 : a.rootDistance != this.rootDistance ? (a.rootDistance > this.rootDistance ? -1 : 1) : 0;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkRule2", 
 function (a) {
return a.massNo < this.massNo ? -1 : a.massNo > this.massNo ? 1 : 0;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkRule3", 
 function (a) {
var b;
var c;
return this.parent == null || !this.parent.isAlkeneAtom2 || !a.parent.isAlkeneAtom2 || this.isDuplicate || a.isDuplicate || !this.isEvenCumulene () || !a.isEvenCumulene () ? -2147483648 : this.parent === a.parent ? this.sign (this.breakTie (a)) : (b = this.parent.getEZaux ()) < (c = a.parent.getEZaux ()) ? -1 : b > c ? 1 : 0;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "isEvenCumulene", 
 function () {
return (this.parent != null && this.parent.isAlkeneAtom2 && ((this.parent.alkeneParent.sphere + this.parent.sphere) % 2) == 1);
});
Clazz.defineMethod (c$, "getEZaux", 
 function () {
if (this.auxEZ == -1 && (this.auxEZ = this.alkeneParent.auxEZ) == -1) {
this.auxEZ = this.getEneWinnerChirality (this.alkeneParent, this, 4, false);
if (this.auxEZ == 0) this.auxEZ = 24;
}this.alkeneParent.auxEZ = this.auxEZ;
if (JU.Logger.debugging) JU.Logger.info ("getZaux " + this.alkeneParent + " " + this.auxEZ);
return this.auxEZ;
});
Clazz.defineMethod (c$, "getEneWinnerChirality", 
 function (a, b, c, d) {
var e = this.getEneEndWinner (a, a.nextSP2, c);
var f = (e == null || e.atom == null ? null : this.getEneEndWinner (b, b.parent, c));
return this.b$["JS.CIPChirality"].getEneChirality (e, a, b, f, d, false);
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,~N,~B");
Clazz.defineMethod (c$, "getEneEndWinner", 
 function (a, b, c) {
var d = a.clone ();
d.addReturnPath (b, d);
var e = null;
for (var f = 1; f <= c; f++) if ((e = d.getTopSorted (f)) != null) break;

return (e == null || e.atom == null ? null : e);
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom,~N");
Clazz.defineMethod (c$, "getReturnPath", 
 function (a) {
var b =  new JU.Lst ();
while (a.parent != null && a.parent.atoms[0] != null) {
if (JU.Logger.debugging) JU.Logger.info ("path:" + a.parent.atom + "->" + a.atom);
b.addLast (a = a.parent);
}
b.addLast (null);
return b;
}, "JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "addReturnPath", 
 function (a, b) {
var c = this.getReturnPath (b);
var d = this;
for (var e = 0, f = c.size (); e < f; e++) {
var g = c.get (e);
if (g == null) {
g = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (null, this, true, this.isAlkene);
} else {
var h = g.sphere;
g = g.clone ();
g.sphere = h + 1;
}d.replaceParentSubstituent (a, g);
if (a == null) break;
a = a.parent;
d = g;
}
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "checkRule4And5", 
 function (a, b) {
return (this.rule4List[a] == null && this.rule4List[b] == null ? 0 : this.rule4List[b] == null ? -1 : this.rule4List[a] == null ? 1 : this.compareMataPair (a, b));
}, "~N,~N");
Clazz.defineMethod (c$, "compareMataPair", 
 function (a, b) {
var c = this.rule4List[a].substring (1);
var d = this.rule4List[b].substring (1);
if (this.b$["JS.CIPChirality"].currentRule == 7) {
c = JU.PT.rep (c, "~", "");
d = JU.PT.rep (d, "~", "");
} else {
var e = false;
var f = (this.b$["JS.CIPChirality"].currentRule == 8);
if (this.atoms[a].nextChiralBranch != null) {
var g = this.atoms[a].getMataList (this.getFirstRef (c), f);
e = (g.indexOf ("|") >= 0);
c = (e ? g : c + g);
}if (this.atoms[b].nextChiralBranch != null) {
var g = this.atoms[b].getMataList (this.getFirstRef (d), f);
e = new Boolean (e | (g.indexOf ("|") >= 0)).valueOf ();
d = (g.indexOf ("|") < 0 ? d + g : g);
}if (JU.Logger.debugging) JU.Logger.info (this.dots () + this + " comparing " + this.atoms[a] + " " + c + " to " + this.atoms[b] + " " + d);
if (f || !e && c.length != d.length) {
return this.sign (c.compareTo (d));
}c = this.cleanRule4Str (c);
d = this.cleanRule4Str (d);
if (e) {
var g = JU.PT.split (c, "|");
var h = JU.PT.split (d, "|");
var i = 2147483647;
var j = 0;
c = g[0];
d = h[0];
for (var k = g.length; --k >= 0; ) {
for (var l = h.length; --l >= 0; ) {
var m = this.compareRule4PairStr (g[k], h[l], true);
j += m;
if (m != 0 && Math.abs (m) <= i) {
i = Math.abs (m);
c = g[k];
d = h[l];
}}
}
if (j == 0) return 0;
}}if (c.length == 1 && "RS".indexOf (c) < 0) {
var e = this.checkEnantiomer (c, d, 0, c.length, " rs");
switch (e) {
case -1:
case 1:
this.canBePseudo = false;
this.doCheckPseudo = true;
return e;
}
}return this.compareRule4PairStr (c, d, false);
}, "~N,~N");
Clazz.defineMethod (c$, "cleanRule4Str", 
 function (a) {
return (a.length > 1 ? JU.PT.replaceAllCharacters (a, "sr~", "") : a);
}, "~S");
Clazz.defineMethod (c$, "getFirstRef", 
 function (a) {
for (var b = 0, c = a.length; b < c; b++) {
var d = a.charAt (b);
switch (d) {
case 'R':
case 'S':
return "" + d;
}
}
return null;
}, "~S");
Clazz.defineMethod (c$, "getMataList", 
 function (a, b) {
var c = 0;
for (var d = this.rule4List.length; --d >= 0; ) if (this.rule4List[d] != null) c++;

var e =  new Array (c);
for (var f = c, g = this.rule4List.length; --g >= 0; ) if (this.rule4List[g] != null) e[--f] = this.rule4List[g];

if (a == null) {
a = this.getMataRef (b);
} else {
for (var h = 0; h < c; h++) e[h] = "." + e[h].substring (1);

}return (a.length == 1 ? this.getMataSequence (e, a, b) : this.getMataSequence (e, "R", false) + "|" + this.getMataSequence (e, "S", false));
}, "~S,~B");
Clazz.defineMethod (c$, "getMataRef", 
 function (a) {
return (a ? "R" : this.rule4Count[1] > this.rule4Count[2] ? "R" : this.rule4Count[1] < this.rule4Count[2] ? "S" : "RS");
}, "~B");
Clazz.defineMethod (c$, "getMataSequence", 
 function (a, b, c) {
var d = a.length;
var e =  new Array (d);
for (var f = d, g = this.rule4List.length; --g >= 0; ) {
if (this.rule4List[g] != null) {
--f;
e[f] = a[f];
if (this.atoms[g].nextChiralBranch != null) e[f] += this.atoms[g].nextChiralBranch.getMataList (b, c);
}}
var h = (c ? e : this.getMataSortedList (e, b));
var i = 0;
for (var j = 0; j < d; j++) {
var k = h[j];
if (k.length > i) i = k.length;
}
var k = "";
var l;
for (var m = 1; m < i; m++) {
for (var n = 0; n < d; n++) {
var o = h[n];
if (m < o.length && (l = o.charAt (m)) != '~' && l != ';') k += l;
}
if (c) {
for (var o = 0; o < d; o++) {
var p = h[o];
if (m < p.length) h[o] = p.substring (0, m) + "~" + p.substring (m + 1);
}
java.util.Arrays.sort (h);
}}
return k;
}, "~A,~S,~B");
Clazz.defineMethod (c$, "compareRule4PairStr", 
 function (a, b, c) {
if (JU.Logger.debugging) JU.Logger.info (this.dots () + this.myPath + " Rule 4b comparing " + a + " " + b);
this.doCheckPseudo = false;
var d = a.length;
if (d == 0 || d != b.length) return 0;
var e = a.charAt (0);
var f = b.charAt (0);
for (var g = 1; g < d; g++) {
var h = (e == a.charAt (g));
if (h != (f == b.charAt (g))) return (c ? g : 1) * (h ? -1 : 1);
}
if (c) return 0;
if (e == f) return -2147483648;
if (!this.canBePseudo) this.b$["JS.CIPChirality"].root.canBePseudo = false;
this.doCheckPseudo = this.canBePseudo && (e == 'R' || e == 'S');
return e < f ? -1 : 1;
}, "~S,~S,~B");
Clazz.defineMethod (c$, "getMataSortedList", 
 function (a, b) {
var c = a.length;
var d =  new Array (c);
for (var e = 0; e < c; e++) d[e] = JU.PT.rep (a[e], b, "A");

java.util.Arrays.sort (d);
for (var f = 0; f < c; f++) d[f] = JU.PT.rep (d[f], "A", b);

if (JU.Logger.debuggingHigh) for (var g = 0; g < c; g++) JU.Logger.info ("Sorted Mata list " + g + " " + b + ": " + d[g]);

return d;
}, "~A,~S");
Clazz.defineMethod (c$, "createAuxiliaryRule4Data", 
function (a, b) {
var c = -1;
var d = "";
var e = (a == null ? "" : "~");
var f = false;
var g = false;
if (this.atom != null) {
this.rule4List =  new Array (4);
var h =  Clazz.newIntArray (4, 0);
var i = 0;
var j =  new Array (1);
for (var k = 0; k < 4; k++) {
var l = this.atoms[k];
if (l != null) l.set ();
if (l != null && !l.isDuplicate && !l.isTerminal) {
l.priority = this.priorities[k];
j[0] = null;
var m = l.createAuxiliaryRule4Data (a == null ? l : a, j);
if (j[0] != null) {
l.nextChiralBranch = j[0];
if (b != null) b[0] = j[0];
}this.rule4List[k] = l.priority + m;
if (l.nextChiralBranch != null || this.isChiralSequence (m)) {
h[i] = k;
i++;
d += m;
} else {
this.rule4List[k] = null;
}}}
var l = 0;
switch (i) {
case 0:
d = "";
break;
case 1:
break;
case 2:
if (a != null) {
l = (this.compareRule4aIsomers (h[0], h[1]));
switch (l) {
case 0:
f = true;
e = "~";
d = "";
break;
case -2147483648:
e = "";
f = true;
l = 0;
break;
case -2:
case 2:
l -= this.sign (l);
d = "r";
case -1:
case 1:
f = true;
g = d.indexOf ("r") >= 0;
d = "";
break;
}
}break;
case 3:
var m = 0;
var n = 0;
var o = 0;
for (var p = 0; p < 2; p++) {
for (var q = p + 1; q < 3; q++) {
o = (this.compareRule4aIsomers (h[p], h[q]));
switch (o) {
case -1:
case 1:
if (l == 0) {
l = o;
m = p;
n = q;
continue;
}p = q = 3;
l = 0;
break;
default:
break;
}
}
}
if (l != 0) {
h[0] = h[m];
h[1] = h[n];
}case 4:
e = "";
f = true;
break;
}
if (f) {
d = "";
if (b != null) b[0] = this;
}if (!f || l == -1 || l == 1) {
if (this.isAlkene) {
if (!f && this.alkeneChild != null) {
var q = (b != null && b[0] === this.alkeneChild);
var r = (((this.alkeneChild.sphere - this.sphere) % 2) == 0);
if (r || this.auxEZ == 24 && this.alkeneChild.bondCount >= 2 && !this.isKekuleAmbiguous) {
c = this.getEneWinnerChirality (this, this.alkeneChild, 8, r);
switch (c) {
case 33:
c = 1;
e = "R";
break;
case 34:
c = 2;
e = "S";
break;
case 8:
c = 1;
e = "R";
break;
case 16:
c = 2;
e = "S";
break;
}
if (c != 0) {
this.auxChirality = e;
this.addMataRef (this.sphere, this.priority, c);
d = "";
if (q) {
this.nextChiralBranch = this.alkeneChild;
b[0] = this;
}}}}} else if (a != null && (this.bondCount == 4 && this.nPriorities >= 3 - Math.abs (l) || this.isTrigonalPyramidal && this.nPriorities >= 2 - Math.abs (l))) {
if (f) {
switch (this.checkPseudoHandedness (h, null)) {
case 1:
e = (l == -1 ? "r" : "s");
break;
case 2:
e = (l == -1 ? "s" : "r");
break;
}
if (g) e = e.toUpperCase ();
this.auxChirality = e;
d = "";
} else {
var q = this.clone ();
if (q.set ()) {
q.addReturnPath (null, this);
q.sortByRule (1);
c = q.checkHandedness ();
e = (c == 1 ? "R" : c == 2 ? "S" : "~");
a.addMataRef (this.sphere, this.priority, c);
}}}}}e += d;
if (JU.Logger.debugging && !e.equals ("~")) JU.Logger.info ("creating aux " + this.myPath + e);
return e;
}, "JS.CIPChirality.CIPAtom,~A");
Clazz.defineMethod (c$, "sortByRule", 
 function (a) {
var b = this.b$["JS.CIPChirality"].root.canBePseudo;
var c = this.b$["JS.CIPChirality"].currentRule;
this.b$["JS.CIPChirality"].currentRule = a;
this.sortSubstituents ();
this.b$["JS.CIPChirality"].currentRule = c;
this.b$["JS.CIPChirality"].root.canBePseudo = b;
}, "~N");
Clazz.defineMethod (c$, "isChiralSequence", 
 function (a) {
return a.indexOf ("R") >= 0 || a.indexOf ("S") >= 0 || a.indexOf ("r") >= 0 || a.indexOf ("s") >= 0 || a.indexOf ("u") >= 0;
}, "~S");
Clazz.defineMethod (c$, "addMataRef", 
 function (a, b, c) {
if (this.rule4Count == null) {
this.rule4Count =  Clazz.newIntArray (-1, [2147483647, 0, 0]);
}var d = a * 10 + b;
if (d <= this.rule4Count[0]) {
if (d < this.rule4Count[0]) {
this.rule4Count[0] = d;
this.rule4Count[1] = this.rule4Count[2] = 0;
}this.rule4Count[c]++;
}}, "~N,~N,~N");
Clazz.defineMethod (c$, "compareRule4aIsomers", 
 function (a, b) {
var c = this.rule4List[a];
var d = this.rule4List[b];
if (c.charAt (0) != d.charAt (0)) return -2147483648;
var e = c.length;
if (e != d.length) return -2147483648;
if (c.equals (d)) return 0;
var f = (c.indexOf ("R") >= 0 || c.indexOf ("S") >= 0);
var g = (f ? "~RS" : "~rs");
if (f) {
c = JU.PT.replaceAllCharacters (c, "rs", "~");
d = JU.PT.replaceAllCharacters (d, "rs", "~");
}var h = this.checkEnantiomer (c, d, 1, e, g);
if (h == -3) {
switch (this.compareMataPair (a, b)) {
case -1:
return -2;
case 1:
return 2;
}
}return h;
}, "~N,~N");
Clazz.defineMethod (c$, "checkEnantiomer", 
 function (a, b, c, d, e) {
var f = 0;
for (var g = c; g < d; g++) {
var h = e.indexOf (a.charAt (g));
var i = h + e.indexOf (b.charAt (g));
if (i == 0) continue;
if (i != 3) {
return -3;
}if (f == 0) f = (h == 1 ? -1 : 1);
}
return f;
}, "~S,~S,~N,~N,~S");
Clazz.defineMethod (c$, "checkPseudoHandedness", 
 function (a, b) {
var c = (b == null ? a[0] : b[a[0]]);
var d = (b == null ? a[1] : b[a[1]]);
var e;
e = this.clone ();
e.atoms[c] = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (null, e, false, this.isAlkene);
e.atoms[d] = Clazz.innerTypeInstance (JS.CIPChirality.CIPAtom, this, null).create (null, e, false, this.isAlkene);
e.addReturnPath (null, this);
e.sortByRule (1);
e.atoms[this.bondCount - 2] = this.atoms[Math.min (c, d)];
e.atoms[this.bondCount - 1] = this.atoms[Math.max (c, d)];
var f = e.checkHandedness ();
if (JU.Logger.debugging) {
for (var g = 0; g < 4; g++) JU.Logger.info ("pseudo " + f + " " + this.priorities[g] + " " + this.atoms[g].myPath);

}return f;
}, "~A,~A");
Clazz.defineMethod (c$, "replaceParentSubstituent", 
 function (a, b) {
for (var c = 0; c < 4; c++) if (this.atoms[c] === a || a == null && this.atoms[c].atom == null) {
this.atoms[c] = b;
if (JU.Logger.debugging) JU.Logger.info ("replace " + this + "[" + c + "]=" + b);
this.parent = a;
return;
}
}, "JS.CIPChirality.CIPAtom,JS.CIPChirality.CIPAtom");
Clazz.defineMethod (c$, "getTopSorted", 
 function (a) {
this.sortByRule (a);
for (var b = 0; b < 4; b++) {
var c = this.atoms[b];
if (!c.sp2Duplicate) return this.priorities[b] == this.priorities[b + 1] ? null : this.atoms[b];
}
return null;
}, "~N");
Clazz.defineMethod (c$, "checkRules4a", 
 function (a, b) {
if (this.isTerminal || this.isDuplicate) return 0;
var c = b.indexOf (this.auxChirality);
var d = b.indexOf (a.auxChirality);
return (c > d + 1 ? -1 : d > c + 1 ? 1 : 0);
}, "JS.CIPChirality.CIPAtom,~S");
Clazz.defineMethod (c$, "checkHandedness", 
function () {
var a = this.atoms[0].atom.getXYZ ();
var b = this.atoms[1].atom.getXYZ ();
var c = this.atoms[2].atom.getXYZ ();
JU.Measure.getNormalThroughPoints (a, b, c, this.b$["JS.CIPChirality"].vNorm, this.b$["JS.CIPChirality"].vTemp);
this.b$["JS.CIPChirality"].vTemp.setT (this.atom.getXYZ ());
this.b$["JS.CIPChirality"].vTemp.sub (a);
return (this.b$["JS.CIPChirality"].vTemp.dot (this.b$["JS.CIPChirality"].vNorm) > 0 ? 1 : 2);
});
Clazz.defineMethod (c$, "sign", 
function (a) {
return (a < 0 ? -1 : a > 0 ? 1 : 0);
}, "~N");
Clazz.defineMethod (c$, "clone", 
function () {
var a = null;
try {
a = Clazz.superCall (this, JS.CIPChirality.CIPAtom, "clone", []);
} catch (e) {
if (Clazz.exceptionOf (e, CloneNotSupportedException)) {
} else {
throw e;
}
}
a.id = this.b$["JS.CIPChirality"].ptID++;
a.atoms =  new Array (4);
a.priorities =  Clazz.newIntArray (4, 0);
a.htPathPoints = this.htPathPoints;
a.doCheckPseudo = false;
for (var b = 0; b < 4; b++) {
if (this.atoms[b] != null) {
a.atoms[b] = this.atoms[b];
}}
a.ties = null;
if (JU.Logger.debugging) JU.Logger.info ("cloning " + this + " as " + a);
return a;
});
Clazz.overrideMethod (c$, "toString", 
function () {
return (this.atom == null ? "<null>" : "[" + this.b$["JS.CIPChirality"].currentRule + "." + this.sphere + "," + this.rootDistance + "." + this.id + "." + this.atom.getAtomName () + (this.isDuplicate ? "*" : "") + "]");
});
c$ = Clazz.p0p ();
};
Clazz.defineStatics (c$,
"NO_CHIRALITY", 0,
"TIED", 0,
"B_WINS", 1,
"A_WINS", -1,
"DIASTEREOMERIC", -3,
"DIASTEREOMERIC_A_WINS", -2,
"DIASTEREOMERIC_B_WINS", 2,
"IGNORE", -2147483648,
"NOT_RELEVANT", -2147483648,
"STEREO_UNDETERMINED", -1,
"STEREO_RS", -1,
"STEREO_EZ", -2,
"STEREO_ALLENE", -3,
"STEREO_R", 1,
"STEREO_S", 2,
"STEREO_M", 33,
"STEREO_P", 34,
"STEREO_Z", 8,
"STEREO_E", 16,
"STEREO_BOTH_RS", 3,
"STEREO_BOTH_EZ", 24,
"RULE_1a", 1,
"RULE_1b", 2,
"RULE_2", 3,
"RULE_3", 4,
"RULE_4a", 5,
"RULE_4b", 6,
"RULE_4c", 7,
"RULE_5", 8,
"ruleNames",  Clazz.newArray (-1, ["", "1a", "1b", "2", "3", "4a", "4b", "4c", "5"]),
"TRIGONALITY_MIN", 0.2,
"MAX_PATH", 50,
"SMALL_RING_MAX", 7);
});
