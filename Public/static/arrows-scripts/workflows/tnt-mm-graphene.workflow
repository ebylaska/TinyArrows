comments: This script defines TNT-4-OH on Graphene AIMD/MM simulations :comments

FOR $A = (       -3.8, -3.6, -3.4, -3.2, 
           -3.0, -2.8, -2.6, -2.4, -2.2,
           -2.0, -1.8, -1.6, -1.4, -1.2,
           -1.0, -0.8, -0.6, -0.4, -0.2,
            0.0, 0.2, 0.4, 0.6, 0.8,
            1.0, 1.2, 1.4, 1.6, 1.8,
            2.0, 2.2, 2.4, 2.6, 2.8,
            3.0, 3.2, 3.4, 3.6, 3.8, 4.0 ) LOOP

Delete all models;
Set text bulk_atoms;
Set text lattice_a1 20.0 0.0 0.0;
Set text lattice_a2 0.0 20.0 0.0;
Set text lattice_a3 0.0 0.0 20.0;
Set text lattice_center 0.0 0.0 0.0;
Unit cell off;

Set text machine eperlmutter;
Set text queue_time 12:00:00;
Set text queue_secret_code 05291999;
Set number queue_ncpus 128;
Set text queue_name serdp;
Set text queue_account mp119;
Set text queue_nwchem_projectname TNT;
Set text queue_nwchem_curdir0 we31869.emsl.pnl.gov:/media/seagate2/Projects/Eric/SERDP/Graphene15;
Set radio wham_posteriori true;
Set url auxiliary_functions https://arrows.emsl.pnnl.gov/api/eric_view/raw=we31869:/media/seagate2/Projects/Eric/SERDP/WHAM/tnt-4-oh.note;

startmol_aux.arrows_script  "TNT + hydroxide --> TNT-4-OH + nitrite" 0.1 $A 5.0;
nsolute frame;

append-graphene.arrows_script C 2.46 15.0 5;
Set text basis_type 100 Ry;

Generate solvated wham input -1.0;

Car-Parrinello
     temperature{300.0} 
     fake_mass{750.0} 
     time_step{5.0} 
      iloop{10} oloop{1000} 
      stime0{10.0}
      motion_name{tequil};

Split submit nwchem;

END FOR LOOP

