
# Generate a Reaction Path
As illustrated in the previous section, it is quite common to hypothesize a chemical reaction network that contains multiple branching pathways that are all thermodynamically favorable.  As a result of this, relying only on reaction energies can be limiting, and approaches to modeling reaction kinetics, e.g. transition-states and reaction pathways are needed.  Unfortunately, these types of calculations involve difficult optimizations that can easily fail.  Even in best case scenarios with an expert user running the calculation, this type of calculation will still end up being 10-20 times more expensive than a reaction energy calculation.  Modeling reactions in solution is even worse.  In addition, transition-states usually contain non-bonding electronic states that are not well described by lower levels of electronic structure theories, and moreover many reactions, even intrinsic one-step reactions, end up having multiple pathways containing multiple barriers.  In short, these calculations are time-consuming and difficult, and not surprisingly, automating calculations for transition-states and reaction pathways is an active area of research.  Even though transition-state and reaction pathway calculation are not completely automated in Arrows, there are several workflows implemented in Arrows that can be used to perform these types of simulations (see the online Arrows manuals \url{https://nwchemgit.github.io/EMSL_Arrows.html#} or 
 \url{https://ebylaska.github.io/TinyArrows/}). 
 
 
 Reaction path simulations are an example of a  molecular simulation that can benefit from the workflow capabilities in Arrows.  As a simple example we demonstrate how to calculate the reaction path energies for the following reaction.
 ```
 carbon dioxide + [HH] --> carbon monoxide + water
```
This is a fundamental reaction for catalysis in which methanol is formed by combining the carbon dioxide with hydrogen gas in the presence of a metal catalyst.

1) enter carbon dioxide + [HH]--> carbon monoxide + water into reaction input in the reaction tab of the Expert Periodic and Molecular editor
2) select build reactants from from chemical reaction button
3) select Generate chemical reaction hash button
4) select Search reaction constraings using reaction hash button
5) Enter min_gamma: -6.0 max_gamma: 6.0 and ngamma: 25
6) select the Builder tab then select Unit cell off button
7) select the JSmol to editor button
8) Move to NWChem Input Editor
9) Enter PMF into project name
10) Enter co2toco into mylabel
11) Enter kitchen:/Projects/CCS into curdir0:
12) select NWChem Format button
13) select Add constraint path button
14) Choose machine, ncpu, ... options
15) Submit NWChem

```
    676004        0       no       no              no      aerosol1           ccs  nwchem-71.nw H2C1O2.out00 curdir=kitchen:/Projects/CCS/PMF/pspw-pbe-H2C1O2-co2toco  1634864673.179590
```
