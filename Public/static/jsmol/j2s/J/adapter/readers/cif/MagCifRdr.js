Clazz.declarePackage ("J.adapter.readers.cif");
Clazz.load (["J.adapter.readers.cif.MagCifRdrInterface"], "J.adapter.readers.cif.MagCifRdr", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.r = null;
Clazz.instantialize (this, arguments);
}, J.adapter.readers.cif, "MagCifRdr", null, J.adapter.readers.cif.MagCifRdrInterface);
Clazz.makeConstructor (c$, 
function () {
});
Clazz.overrideMethod (c$, "initialize", 
function (r) {
this.r = r;
}, "J.adapter.smarter.AtomSetCollectionReader");
});
