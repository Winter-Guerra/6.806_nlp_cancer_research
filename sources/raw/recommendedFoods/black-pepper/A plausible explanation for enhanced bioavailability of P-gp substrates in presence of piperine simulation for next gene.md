# A plausible explanation for enhanced bioavailability of P-gp substrates in presence of piperine: simulation for next generation of P-gp inhibitors

## Abstract

P-glycoprotein (P-gp) has a major role to play in drug pharmacokinetics and pharmacodynamics, since it effluxes many cytotoxic hydrophobic anticancer drugs from gastrointestinal tract, brain, liver and kidney. Piperine is known to enhance the bioavailability of curcumin, as a substrate of P-gp by at least 2000 %. Besides these at least 50 other substrates and inhibitors of P-gp have been reported so far. All P-gp inhibitors have diverse structures. Although little is known about binding of some flavonoids and steroids at the NBD (nucleotide binding domain) of P-gp in the vicinity of ATP binding site inhibiting its hydrolysis, a valid explanation of how P-gp accommodates such a diverse set of inhibitors is still awaited. In the present study, piperine up to 100 μM has not shown observable cytotoxic effect on MDCK cell line, and it has been shown to accumulate rhodamine by fluorescence microscopy and fluorescent activated cell sorter in MDCK cells. Computational simulation for piperine and some first and second generation P-gp inhibitors has shown that these dock at the NBD site of P-gp. A comparative simulation study has been carried out regarding their docking and binding energies. Binding conformation of P-gp co-crystallized complexes with ADP, AMP-PNP (Adenylyl-imidodiphosphate), and ATP were compared with piperine. The receptor based E-pharmacophore of docked piperine has been simulated to find common features amongst P-gp inhibitors. Finally it has been concluded that piperine could be utilized as base molecule for design and development of safe non-toxic inhibitor of P-gp in order to enhance the bioavailability of most of its substrates.


Piperine binds between the consensus sequence of Walker A/P loop and Walker C loop (linker peptide) at the nucleotide binding domain which is crucial for ATP coupled efflux through P-gp. ATP binding competes with piperine. This explains why piperine enhances the bioavailability of its substrate like curcumin by 2000 %

### Electronic supplementary material

The online version of this article (doi:10.​1007/​s00894-012-1535-8) contains supplementary material, which is available to authorized users.

### Keywords

Docking E-pharmacophores Homology modeling Immunofluorscence P-glycoprotein (P-gp) P-gp inhibitors Piperine

## Introduction

Large number of hydrophobic drugs have poor bioavailability due to efflux through MDR (multidrug resistance) proteins. Major reasons contributing to the low plasma and tissue levels of P-gp substrates appear to be due to rapid systemic elimination. However, in the presence of the P-gp inhibitors numerous substrates have shown enhanced bioavailability. Piperine is an alkaloid present in black pepper. Piperine enhances bioavailability of curcumin [1], phenytoin, propanol, theophylline [2] and rifampicin [3]. Influence of Trikatu (having piperine as an ingredient) on rifampicin bioavailability was studied by Dhanukar et al. [4].

P-gp is organized in two homologous halves, each half begins with a TMD (TM transmembrane domain) containing six TM segments followed by a hydrophilic nucleotide-binding domain [5] (Fig. 1). ATP cassettes/domain of P-gp is composed of ATP binding site (Walker B Loop, D Loop, Q Loop, and H-Loop/Switch Region), ABC transporter (also called walker C motif or linker peptide) and Walker A/P loop. Linker peptide is thought to be involved in ATP hydrolysis as a γ- phosphate center and/or as a signal to membrane spanning domains. Walker A/P loop having consensus sequence GxxGxGKST forms a loop which binds to alpha and β-phosphates or di and trinucleotides. The two ATP molecules bind at the interface between the Walker A sites (GxxGxGKST) and Walker C motif or linker peptide (LSGGQKQRA) sequences of NBDs [6].



The cavity of NBDs shares binding sites for both ATP as well as inhibitors; as steroids and flavonoids do [7, 8] whereas substrates (cytotoxic and hydrophobic drugs of therapeutic importance) have different binding sites. Numerous P-gp substrates (anticancer drugs, cardiovascular drugs, antiviral drugs, antibacterial agents, GIT drugs and several other drugs) are effluxed through P-gp as summarized by Vishal et al. [9].

In the present work a plausible explanation has been given for the enhanced bioavailability of P-gp substrates in presence of piperine. Attempt has been made to utilize the available data to correlate development of 1st, 2nd and 3rd generation of inhibitors with their docking scores at NBD domain. 3D structure of P-gp complexed with ADP [10], AMP-PNP [11] and ATP [12] has been used for comparative study of binding with docked complex of P- gp- piperine.

## Materials and methods

### Reagents and culture methods

MDCK cells were obtained from NCCS and grown in MEM media, supplemented with 10 % FCS, 2 % sodium pyruvate, 1 % pencillin, and 1 % streptomycin. Cells were grown in T-25 flasks to 80 % confluency at 370 C humidified atmosphere of 5 % CO2 and humidified air. Cells were routinely trypsinized (0.05 % trypsin/EDTA) and subcultured.

### Cell culture and drug treatment

Stock solution of piperine was prepared in DMSO and stored at −200 C. Stock was diluted in the range of 10 μm to 100 μM concentrations. Exponentially growing cells were seeded at the densities that allowed untreated cells to reach 75–80 % confluent state. Cells were treated with piperine in fresh media after 24 h of plating.

### Cell viability assay

Cytotoxic effect of piperine on MDCK cell line was determined by the trypan blue staining, counting the viable cells on hemocytometer. MDCK cells (1 × 104 cells/well) were seeded in 12 well plates. After 24 h of plating the cells were exposed to increasing concentrations of piperine ranging from 10 μM to 100 μM in serum free media, both attached and non attached cells were collected and resuspended in phosphate buffered saline (PBS). The IC50 concentrations were determined from concentration response curve.

### Rhodamine efflux assay

The cells were seeded on coverslips in six well plates for 24 h following treatment with piperine and 1 μg/ml of rhodamine, after 1 h of incubation at 37 0 C, cells were washed twice with PBS, mounted and inspected by fluorescence microscopy [13]

### Immunofluorscence

Rhodamine, a fluorescent dye was used to monitor the piperine induced accumulation of rhodamine in cells described previously [14]. MDCK cells were seeded at density 4 × 104cell/well in six well plates for 24 h. After approaching 90 % confluency, cells were co-treated with rhodamine (10 μM) and piperine (0–100 μM) for 30 min at 370 C. The supenatant was removed, and the cells were harvested and suspended in PBS. Measurement of accumulated rhodamine due to piperine in each sample was analyzed by FACS (fluorescent activated cell sorter) and 10,000 cells were counted.

### Homology modeling

Human P-gp amino acids reference sequence [gi|42741659|ref|NP_000918.2] (http://​www.​ncbi.​nlm.​nih.​gov/​protein/​NP_​000918.​2) was taken from NCBI protein ref sequence database. Homology modeling module Prime (Prime 2.2, Schrödinger, LLC, New York, NY, 2011) was used for modeling as follows: (a)Query sequence (NP_000918.2) was imported into the structure prediction window. HAMMER/Pfam program was used to search for sequence patterns in-build in prime. It generates hidden Markov model (HMM) from a multiple sequence alignment and is used to identify the query family and provides information about which residues are conserved in the consensus sequence. (b) Finding sequence homologs: To find sequence homologue PDB BLAST was performed and as template 2HYD was selected along with ADP. Structure of human P-gp is available (PDB ID 3G60, 3G5U and 3G61) but none of the structure is complexed with ATP/ADP at NBD, therefore 2HYD was selected for study. PDB BLAST has shown total score e-value, maximum identity 501, 2e-76 and 34 % respectively. However the maximum identity, e value, and positives at NBD domain, i.e., from 392 to 629 was 120/234 (51 %), 1e-62, 142/234 (61 %) is quite well to produce a reliable model. (c) Build structure steps: It closes gaps, and predicts side-chain conformations of non-conserved residues to produce a model of local energy minima conformation with no clashes. The structure produced in the previous step is representing only local energy minima not the global minima. Therefore, regions with gaps in the alignment were refined in the next step. (d) Refinement step: In the first refinement phase, default sampling method was used for loop size of less than five residues and for refinement of more than five residues, extended sampling method was used. Obtained model was validated (http://​nihserver.​mbi.​ucla.​edu/​SAVES/​).

### Clustering of the P-gp inhibitors

Canvas module of Schrodinger was used to simulate fingerprints or molecular properties using hierarchical clustering algorithm. All inhibitors (1st/2nd generation inhibitors: amiodarone, astemizole, atorvastatin, bepridil, chlorpromazine, clarithromycin, cortisol, cyclosporine, diltiazem, dipyridamole, disulfiram, erythromycin, felodipine, itraconazole, ketoconazole, midazolam, nicardipine, nitrendipine, progesterone, quinidine, quinine, reserpine, ritonavir, sirolimus (rapamycin), tacrolimus, tamoxifen, terfenadine, tetrabenazine, valinomycin, verapamil, vinblastine and 3rd generation inhibitors Biricodar (VX-710), LY335979, GF120918, OC144-093, R101933, Valspodar (PSC 833), XR9051) published in pharmacotherapy journal [15] were clustered using linear finger print and Tanimoto similarity to cluster in seven classes based on the similarities (Canvas 1.4, Schrödinger, LLC, New York, NY, 2011).

### Ligand preparation

The 2D structures of P-gp inhibitors were generated by drawing on ChemSketch (www.​acdlabs.​com) and 3-D structures from CORINA server (http://​www.​molecular-networks.​com/​) and further optimized. Ligprep module of Schrödinger was used to generate energy minimized 3D structures using OPLS-2005. To correct Lewis structure and tautomeric and ionization states (PH 7.0 +/− 2.0) default settings were used (Ligprep, Schrödinger, LLC, New York, NY, 2011).

### Protein preparation

3D structure of modeled P-gp was prepared using protein preparation wizard (Maestro 10.0 Schrödinger, LLC, New York, NY, 2011). Bond order and formal charges were assigned and hydrogen was added. His (histidine) tautomers and ionization states were predicted, hydroxyl and thiol hydrogens were sampled. For structures with missing side chain atoms the refinement module prime, was used to predict their conformation. Further to refine the structure OPLS-2005 force field parameter was used to alleviate steric clashes and the minimization was terminated when RMSD reached maximum cutoff value of 0.30 Å. Binding site was defined by centroid of ADP, midpoint of grid box (101.64:52.61:168.97) and dimensions were set to 15 Å. Hydroxyl rotatable groups enclosed in the grid were sampled. For grid preparation and docking at TMD domain centroid of complexed ligand was taken (PDB: 3G60).

### Docking study with Glide

Docking was performed at the nucleotide binding site of NB domain where inhibitor binding shared with ATP binding site using Glide module of Schrödinger (Glide, version 5.7, Schrödinger, LLC, New York, NY, 2011) and also docked at the TMD of human P-gp (3G60) complexed with a inhibitor. All inhibitors were set for docking with stranded docking precision (SP Glide), further it was used to refine the docked poses with option to output Glide XP descriptor information (Maestro 10.0 Schrödinger, LLC, New York, NY, 2011).

### Hypothesis generation for energy-optimized structure-based pharmacophores: (E-pharmacophores)

E-pharmacophore was generated using default chemical features: hydrogen bond acceptor (A), hydrogen bond donor (D), hydrophobe (H), negative ionizable (N), positive ionizable (P), and aromatic ring (R). Hydrogen bond acceptor and donor sites were represented as vectors. Each pharmacophore feature site is first assigned an energetic value equal to the sum of the Glide XP contributions of the atoms comprising the site to be quantified and ranked on the basis of these energetic terms used in Glide XP descriptors (Glide, version 5.7, Schrödinger, LLC, New York, NY, 2011).

### Docking study with AutoDock

Docking was also performed with AutoDock which efficiently docks macro-cyclic ligand with a large number of flexible bonds while Glide docking module is more efficient for molecules with fewer number of rotatable bonds. These inhibitors were docked at the nucleotide binding domain using AutoDock 3.0 [16, 17]. Grid size was set to include significant portions of the surrounding surface of nucleotide binding domain in each simulation. The dimensions of the grids for nucleotide binding site were set to 72 Å in each dimension, with a spacing of 0.375 Å between the grid points and the center of grid (101.64:52.61:168.97) was taken form crystal structure. The default AutoDock run parameters were as follows: the maximum number of energy evaluations, the maximum number of generation in the genetic algorithm and the number of GA per run were 2,500,000, 2,700,000 and 50 respectively. All other run parameters were maintained at their default settings. As far as the search methods are concerned, genetic algorithm was used [17].

### 2D plot of complexed structure

Ligplot [18] and HBPLUS [19] were used to generate 2D plot of the docked conformations to find out hydrogen bond and hydrophobic interactions.

## Results

Piperine has been tested for its cytoxicity/cell viability in MDCK cell line which overexpresses P-gp. Piperine treated MDCK cells survive for a longer time than piperine untreated cells, i.e., this molecule has survival advantage when cells are deprived of nutrition (Fig. 2).


Survival benefit of piperine over MDCK cell line. Untreated cells have shown decrease in percent cell viability after 90 h while piperine exposed cells have not only shown non-cyotoxic effect but also manage to survive for longer time

To quantify the enhancement of bioavailability by piperine, cells were treated with rhodamine and monitored by FACS. At higher concentration of piperine, rhodamine accumulation increased by two fold (Fig. 3a &amp; b), confirming that piperine is an inhibitor of P-gp. In order to assess drug accumulation on treatment with piperine, the cells were analyzed by fluorescence microscopy (Fig. 4a &amp; b). Rhodamine accumulation in mitochondria and cytosol was found to be higher comparable to control at higher concentrations of piperine.


Accumulation of rhodamine dye on treatment of piperine measured by FACS. (a) Bar diagram showing increased accumulation of rhodamine on treatment with 20–140 μg of piperine. (b) Overlay picture of FACS at 120–140 μg of piperine treatment


Rhodamine accumulations on treatment of piperine (a) cells were treated only with rhodamine and (b) rhodamine and piperine. Rhodamine accumulation is clearly observed in the surrounding of nuclear membrane as well as in cytosol. All pictures were taken at 40X on inverted microscope

### Homology modeling

PDB Blast of the human P-gp reference sequence with bacterial ABC transporter (Sav1866) from _Staphylococcus aureus_ (PDB ID: 2HYD) sequence having 3 Å resolution has given BLAST score (679), expect 7e-77, identities 171/497 (34 %), positives 263/497 (53 %), gaps 10/497 (2 %). _S. aureus_ (PDB ID: 2HYD) was used as template for human P-gp protein modeling. Obtained model has shown overall quality factor of 92.032 (Fig. 1S). Ramachandran plots of model has shown that core regions, additionally allowed regions, generously allowed regions and disallowed regions were 91.6 %, 7.5 %, 0.9 %, 0.0 % respectively.

#### Modeling for binding site

Cavity of P-gp nucleotide binding site was simulated by molegro software [20]. The two nucleotide binding sites have shown cavity size of 427.008 Å3 and 338.944 Å3. NBD domain where ADP is complexed was selected for docking (Fig. 5).


Modeled human P-gp along with ADP and amino acids close ADP. Cavity of NBD domain of P-gp was simulated by molegro shown in green mesh

#### Comparison of binding of ATP, AMP-PNP, ADP and docked complex of piperine at NBD site

In order to find out whether piperine also binds at NBD domain of P-gp, it was docked and amino acid residues lying 3Ǻ close to NBD were compared with ADP, ATP, AMP-PNP from their X-ray crystallographic complexes and with docked P-glycoprotein-piperine complex. Docking simulation has shown that all conformers of piperine bind in single mode at the nucleotide binding site. 2D plot of X-ray crystallographic structure of co-crystallized ATP, ADP &amp; AMP-PNP with P-gp have shown that they share common residues Y349B, I356B, G377B, G379B, K380B, S381B, K477A as piperine does (Fig. 6d). It indicates that binding of piperine is similar to ATP, ADP and AMP-PNP bindings (Table 1).


2D plot of AMP-PNP, ATP and ADP complexed with NBD of multidrug transporter and docked complex of piperine at NBD of PDB ID-2HYD. Amino acids which are in close contact to ligand are shown (a) 2D plot of ABC transporter sav1866 from _S. aureus_ (PDB ID-2ONJ) complexed with AMP-PNP at the NBD binding site. (b) 2D plot human multidrug resistance protein 1 (PDB_ID: 2CBZ) complexed with ATP, Mg and HOH (Water) at the NBD binding site. (c) 2D plot of multidrug ABC transporter sav1866, PDB ID 2HYD complexed with ADP at the NBD binding site (d) Docked compelx of piperine at the NBD of 2HYD showing binding mode of the molecule and amino acid stablizing the complexs




#### Docking study of 1st and 2nd/3rd generation inhibitors

P-gp inhibitors were docked at the NBD of P-gp which have hydrophobic cavity where small steroid like molecules bind whereas flavonoids binding is shared with ATP binding site as well as steroid binding site [7, 8, 21–24]. Docking energies of piperine and its conformation indicate how it docked at the NBD site. Docking conformation of all inhibitors is shown with E-pharmacophore features in Fig. 2S.

In our docking study with Glide, docking energy of ATP is nearly −12.18 kcal mol−1 (Table 2). Most of the new generation inhibitors have docking energies closer to −11 kcal mol−1 except R101933 (−5.59). LY335979, GF120918, Biricodar (vx-710) having docking energies −11.42, −11.37, −11.26 kcal mol−1 respectively. Third generation inhibitor biricodar is a clinically important molecule which has docking score −11.26 equal to AMP-PNP and higher to AMP (−10.47).


Glide dock score (−kcal mol−1) of 1st and 2nd/3rd generation inhibitors at NBD site  


All scores are given in kcal mol−1; 3rd generation inhibitors are marked with () star

Docking was also performed at the TMD domain of P-gp (PDB ID 3G60) where it is complexed with ligand OJZ: (4R,5R,11R,12R,18R,19 S)-4,11,18-tris(1-methylethyl)-6,13,20-triselena-3,10,17,22,23,24-hexaazatetracyclo[17.2.1.1 ~ 5,8 ~ .1 ~ 12,15~] tetracosa-1(21),7,14-triene-2,9,16-trione. Similar SP/XP-Glide docking protocol was followed except, center for grid generation was set to the centroid of complex ligand OJZ, i.e., X, Y and Z: coordinates were 19.091, 52.349 and −0.277 respectively. The glide docking results are summarized in Table 3.


Docking score (−kcal mol−1) of 1st and 2nd/3rd generation inhibitors at TMD of pg-P (PDB ID 3G60)  


However docking score obtained with AutoDock favors clinical developmental progress made in the direction of 2nd and 3rd generation of inhibitors. Descending orders of their docking energies (kcal mol−1) are Biricodar-vx-710 (−18.46), R101933 (−17.52), XR9576 (−17.52), OC144-093 (−16.7), GF120918 (−15.32) and LY335979 (−13.42). To summarize, inhibitors of P-gp were docked and docked conformations of highest priority were plotted by ligplot software. Presence of these residues at binding site could be used as reference for docking and virtual screening for next generation of P-gp inhibitors.

### E- pharmacophore

#### Clustering of the P-gp inhibitors

Since P-gp inhibitors are diverse set of active molecules therefore we prepared hierarchical cluster into seven classes. These clusters are cluster_1: ADP, ATP and AMP-PNP cluster_2: itraconazole, ketaconazole and chloropromazine cluster_3: ritonavir, nicardpine, terfenadine, tetrabenzene, tamoxifen and bepridil cluster_4: LY335979, quanidine, vinblastine and quinine cluster_5: cortisol, progestreron, clarithromycin, sirolimus, tacrolimus and erthromycin cluster_6: XR9576, GF120918, R101933, biricodar (VX-710), reserpine, aestimizole and amiodarone cluster_7: OC144-093 and piperine. Disulfiram and dipridamole have unique structure these do not belong to any cluster. All these clusters were docked with SP glide and refined with XP glide scoring function using energy based descriptors. Energy based pharmacophore (E-pharmacophore) shown in Fig. 3S(a–f) and Table 4. The most favorable interaction shown by inhibitors of clusters 2,3,4,6 and 7 are their aromatic regions R35, R42, R58, R87, R18 of the NBD where purine ring of ATP/ADP binds. These aromatic regions (R35, R42, R58, R87 and R18) shown by orange ring have spatial distance in range of 11–13 Å with negative ionizable center (Fig. 3Sa).


E-pharmacophore features of P-gp inhibitors and scores (N: negative center, R: aromatic, A: acceptor, D: donor, and H: hydrophobic feature)  



E-pharmacophore feature of the inhibitors of highest docking score, i.e., LY335979 (−11.42), GF120918 (−11.37) and Biricodar-Vx-710 (−11.26) suggest that R41 and R49/R45 is a must match site with spatial distance of 11 Å (Fig. 4S). E-pharmacophores of all active inhibitors have been given in Fig. 5S.

### Binding of piperine and ADP AMP-PNP and ATP

Docked conformaton of piperine and ADP (Fig. 7a) and docked conformation of ADP AMP-PNP and ATP (Fig. 7b) showing that either of the two conformations (R60/R61) could be achived by aromatic ring of purine separated by distance of 11.026 Å. This explains piperine might be competiting with the ADP/ATP during efflux process.


(a) E-pharmacophore and binding mode of piperine aligned with ADP (b); E-pharmacophore and binding mode of ATP, ADP and AMP-PNP, showing conformation of purine moiety which could take either of two conformations

## Discussion

P-gp plays a significant role in the bioavailability of several drugs mainly cytotoxic hydrophobic and anticancerous drugs. Cell viability/cell cytotoxicity assay in the presence of piperine in MDCK cell line has shown that piperine treated cells are more viable than untreated cells. It indicates that piperine is not toxic even at higher doses and has survival benefits in loss of growth media. Effect of piperine was also studied in MCF-7 (a breast cancer cell line), U87/U373 (brain tumor cell lines), where it has not shown any undesirable effect upto 100 μM (cell viability/toxicity data is not shown). Piperine treatment causes accumulation of fluorescent dye rhodamine as shown by fluorescence microscopy and fluorescent activated cell sorter. These finding indicate that piperine might be competing with ATP or binding in close vicinity of ATP binding site like steroids and flavonoids [7, 8].

PDB BLAST for human P-gp reference sequence [gi|42741659|ref|NP_000918.2] was performed. PDB ID 3G60 and 3G5U has shown query coverage of 99 % and zero e-value but these structures do not get complexed with nucleotide (ADP/ATP/AMP-PNP). Thereby available human X-ray crystallographic P-gp structures are unable to provide actual conformation of NBD domain, its cavity and binding mode of ATP/ADP. Hence to obtain a 3D structure of human P-gp complexed with nucleotide (ADP) it was modeled, using 2HYD as template. It was modeled with an overall quality factor of 92.032. However identity of human and bacterial efflux protein is 34 %, but have very high positive 53 % score. This is why the obtained modeled structure has very high accuracy.

Modeling of nucleotide binding site has shown a huge cavity of (~427 Å3) [20] which can accommodate inhibitors of high molecular weight along with ATP. Steroids and flavonoids like molecule have affinity to the vicinal site of ATP binding sites reported by Di Pietro et al. and Conseil et al. [7, 8]. Docking with glide and AutoDock has shown that most of the 3rd generation inhibitors and P-gp inhibitor of clinical use, i.e., biricodar (vx-710) dock well with higher scores than most of the 1st and 2nd generation inhibitors at NBD domain. It indicates that these inhibitors do bind at ATP binding site of NBD of P-gp and inhibit efflux. In order to find out whether piperine also binds at NBD domain of P-gp, it was docked and it was found that amino acid residues lying 3-4Ǻ close to NBD are comparable with ADP, ATP, ADP-PNP complexed with P-gp protein. Significant amino acids residues in docked conformations at the nucleotide binding site indicate that molecules have effective interaction with NBD. Higher docking score suggests that the molecule could be considered as lead molecule and this active entity could be used for development of the inhibitors of next generations.

Docking simulation with glide-SP/XP module has shown that ligands (Clarithromycin; mol. wt. 749.9, Sirolimus; mol. wt. 901, Tacrolimus mol wt. 804; Valinomycin; mol. wt. 1111.3 and Erthromycin mol wt; 733.9) do not dock at NBD site. AutoDock also does not show docking at NBD for these ligands except clarithromycin tacrolimus with very poor docking and binding energies. These molecules, having macrocylic rings with high molecular weight, might be possibly binding to the channel of cytosolic transmembrane domain of P-gp; thereby plugging the efflux passage of P-gp substrates. Docking study of P-gp inhibitors close to the ATP binding site has shown that these share common residue at the binding site as indicated by the residues in the X-ray crystallographic structure. Some 1st generation inhibitors have shown single mode of binding, i.e., all the conformers bind in a single mode.

However, there are several reports and co-crystallized structure PDB ID (3G60, 3G61 and 3G5U) indicates that inhibition of efflux through P-gp is due to binding of the P-gp inhibitor at TMD domain of protein. Hence these inhibitors were docked at the TMD domain of P-gp at the centeroid of ligand (X:19.09, Y:52.35, _Z_ = −0.27) complexed in TMD domain (PDB ID) via Glide module(SP and XP) of Schrodinger. The docking scores are not in favor of 3rd generation inhibitors (Table 3). Docking study indicates that NBD is a site of inhibitor binding while TMD domains, which make passage/channel for the efflux of P-gp substrates. Clarithromycin, Tacrolimus, Valinomycin, and Erthromycin do not dock at NBD or have very poor docking scores of these ligands which indicates that these molecules do not bind at NBD domain and higher docking score at TMD domain (Erthromycin -9.84; Tacrolimus-11.36, Sirolimus-10.97) indicates that these molecules might be occluded somewhere in the TMD passage thereby inhibiting efflux of P-gp substrates.

Docked conformation of piperine has shown that it binds with the consensus sequence (1070GxxGxGKST1078), i.e., residues (S1072, G1073, C1074G, G1075, K1076, S1077,T1078) of walker A/P loops which also participate in the binding of α and β-phosphates or di and tri-nucleotides of ADP/ATP. Loop (IVSQ) contains invariant Gln stabilizes P-gp ATP complex, which is thought to be attacking at ATP nucleotide. Histidine-1232 residue participating in binding of piperine might be interfering with the polarization of water molecule. Piperine docked at the NBD2 site binds with consensus sequence (1070GxxGxGKST1078) and its opposite linker region (531LSGGQ535). Docked conformation of piperine has shown that it binds with Walker A and Walker C consensus sequences. Binding of piperine might be competing with ATP which is required for energy coupled efflux of its substrate.

E-pharmacophore feature of the cluster-1 suggests that one negative and an aromatic feature with the spatial distance of 11–13 Å is needed to be a class of absolute Pg-p inhibitors that could be analogs of ADP/ATP (Table 4). Negative feature is a center where γ and β phosphate groups of ATP bind to the receptor and get hydrolyzed to ADP for efflux of P-gp substrate. The aromatic features (R74, R35, R42, R58, R87, R18 &amp; R41) are a must match site occupied by all cluster groups (Fig. 3S(a–f)) and (Fig. 4S). E-pharmacophore of verpamil and ADP has shown negative center N37 = −1.45 and N38 = −5.48; Donor: D20 = −1.60 and D19 = −1.59, Aromatic: R49 = −0.89, R46 = −0.79 two each and one acceptor site A18 = −0.51. Among these sites two aromatic features are common for all inhibitors (Table 4). Based on the docking score at NBD as well as TMD (Tables 2 &amp; 3) and E-pharmacophore it could be concluded that verapamil binds to the NBD domain (Fig. 3Sg). E-pharmacophore feature of the inhibitors of highest docking score, i.e., LY335979 (−11.42), GF120918 (−11.37) and Biricodar-Vx-710 (−11.26) suggest that R41 and R49/R45 are a must match site with spatial distance of 11 Å (Fig. 4S)

E-pharmacophores of all inhibitors have been shown in Fig. 5S. The scores of features R177, R155, R164, R118, R162, are −2.40, −145, −1.25, −1.77, −0.79, and −0.73 respectively and represent all the clusters. If a molecule satisfies the R177 and either of the R155 or R164 feature it could be a potential inhibitor. The R177 and R164 are also pharmacophoric features of Bircodar, a 3rd generation inhibitor preferred by clinicians to enhance the bioavailability of several substrates. R177 and R164 are a most preferred site for purine ring of ATP/ADP which could bind at either R177 or R164 site of NBD domain. This is also the case of other 3rd generation of inhibitors GF120918 and LY335979 and several other first generations of inhibitors nicardpine, amidarone, reserpine, verapamil, OC- OC144-093 and ketaconazole.

E-pharmacophores have shown that ATP/ADP and piperine have a similar mode of binding (R24 −1.73, N22-1.26, A6-1.21, D14 −1.21, R23 −0.66, A13 −0.17, A8 −0.38) (Fig. 3Sa). Binding of piperine to the NBD site share common residues like other P-gp inhibitors and the entire docked conformers bind in a single mode given by both docking methods used in this study. These findings explain the observation of Shoba et al., i.e., why piperine enhances bioavailability of curcumin by 2000 %.

## Conclusions

Piperine has shown survival benefits over untreated MDCK cell line and also induces accumulation of P-gp’s substrate rhodamine. Higher docking and binding scores of 2nd/3rd generation inhibitors in comparison to 1st generation inhibitors suggest that nucleotide binding domain is the only site for P-gp inhibitors except macrocyclic inhibitors. Higher scores of 3rd generation inhibitors justify why these are so called 3rd generation inhibitors. Therefore it was concluded that P-gp inhibitors could be classified as first; inhibitors that bind at NBD domain second; inhibitors which probably bind in the transmembrane domain blocking the passage of efflux channel. Crystallized complex of P-gp with ADP, ATP, and AMP-PNP and docked-complex of piperine share common amino acids at the binding site confirming that piperine also binds in close proximity to nucleotide binding domain. All these findings suggest that P-gp inhibitors bind in the vicinity of ATP binding site. Considering the E-pharmacophore and structural features of piperine and active entity of other inhibitors, which have shown better or equivalent docking scores, could be taken for the development for next generation of P-gp inhibitors. As a conclusion most potent P-gp inhibitors can be developed based on piperine as a base molecule.

## Electronic supplementary material





