############## Authors ###########

Malo Le Boulch
Patrice Déhais
Sylvie Combes
Géraldine Pascal

GenPhySE & Sigenae, Université de Toulouse, INRA, INPT, ENVT, Castanet Tolosan, France

############## Description  ###########
MACADAM database is a collection of metabolic pathways and functional annotations linked to taxonomic information.
It can be queried  by organism name or using metabolic information.

############## Citations ###########
If you use MACADAM database for your work, please cite:
ARTICLE

You can also cite:

    MetaCyc database: Ron Caspi, Tomer Altman, Richard Billington, Kate Dreher, Hartmut Foerster, Carol A. Fulcher, Timothy A. Holland, Ingrid M. Keseler, Anamika Kothari, Aya Kubo, Markus Krummenacker, Mario Latendresse, Lukas A. Mueller, Quang Ong, Suzanne Paley, Pallavi Subhraveti, Daniel S. Weaver, Deepika Weerasinghe, Peifen Zhang, Peter D. Karp;  The MetaCyc database of metabolic pathways and enzymes and the BioCyc collection of Pathway/Genome Databases, Nucleic Acids Research, Volume 42, Issue D1, 1 January 2014, Pages D459–D471, https://doi.org/10.1093/nar/gkt1103

    FAPROTAX: Louca, S., Parfrey, L.W., Doebeli, M. (2016) - Decoupling function and taxonomy in the global ocean microbiome. Science 353:1272-1277

    (IJSEM) phenotypic database: Barberán A, Caceres Velazquez H, Jones S, Fierer N. Hiding in Plain Sight: Mining Bacterial Species Records for Phenotypic Trait Information. mSphere. 2017;2(4):e00237-17. Published 2017 Aug 2. doi:10.1128/mSphere.00237-17



############## Licence ###########

FAPROTAX and IJSEM Phenotypic databases have only been modified in order for them to be integrated into MACADAM

############## Required dependencies ###########
For the python script:
python 3 (Written in python 3.5 but 3.7 works) (https://www.python.org/downloads/)
sqlite3 module for python3

To open the sqlite database you can use SQLite browser (https://sqlitebrowser.org/dl/)


############## Arguments  ###########
All input can be partial (except in the case of a taxonomy, when -strict is used)
Separator is coma


-prefix: prefix for the output
-tax: taxonomy of interest. If there are multiple taxonomies, they must be separated by commas.
-func: name of the pathways/functional annotations of interest separated by commas
-MTB: compounds of interest separated by commas
-rxn: reactions of interest separated by commas
-enz: enzymes of interest separated by commas
-rank: taxonomic ranks of interest (species, genus, family, order, class, phylum)
-min: minimum completeness score of a metabolic pathway
-max: maximum completeness score of a metabolic pathway
-nonscientific: allow non scientific names (Warning: can cause mismatches)
-strict: strict compliance with the taxonomical input.
-verbose: output another more detailed file. For debugging
-EC: EC Numbers of interest separated by commas



############## Examples of usage with python script  ###########
Install python 3 and add it to your path.
Open a command prompt.
Browse to the directory with the MACADAM database in it.
The result file will be createdin the Results directory with the name indicate in -prefix.
Here is some example of command

From the article:
Fig 6, A:
All Staphylococcus aureus and Kitasatospora aureofaciens with a focus on urea pathways:
python MacadamExplore.py -tax "staphylococcus aureus,Kitasatospora aureofaciens" -strict true -rank species -prefix Staphy -func urea

Fig 6, B:
Lactobacillus cerevisiae with a focus on urea pathways:
python MacadamExplore.py -tax "lactobacillus cerevisiae" -strict true -rank species -prefix Cerevi -func urea

Usage of strict:
When strict parameters is set to true (“-strict true”) MACADAM Explore search the exact taxonomy requested in tax option.
Example:
Kitasatospora aureofaciens will output results for Kitasatospora aureofaciens in strict true or false.
Kitasatospora aureofacien (without “s”) will output results for Kitasatospora aureofaciens in strict false only.

Also in strict mode if a species do not have functional information then MACADAM do not show information for the upper rank.
Example:
Staphylococcus caprae don’t have any functional information MACADAM.
In strict mode (“-strict true”), the result file will contain no functional information.
In -strict false, the upper rank (Staphylococcus) functional information will be shown.


Usage with function
python MacadamExplore.py -tax "staphylococcus aureus,Kitasatospora aureofaciens" -strict true -rank species -prefix Staphy -func urea
The result file will only show the pathway containing the word urea

Usage with reaction
python MacadamExplore.py -tax "staphylococcus aureus,Kitasatospora aureofaciens" -rank species -prefix Staphy -rxn pyra
The result file will only show the pathway containing the reactions containing the word "pyra"

Usage with enzymes
python MacadamExplore.py -tax "staphylococcus aureus,Kitasatospora aureofaciens" -rank species -prefix Staphy -enz phos
The result file will only show the pathway containing the enzymes containing the word "phos"

Usage with ranks
python MacadamExplore.py -tax "staphylococcus,Kitasatospora" -rank genus -prefix Staphy
The result file will only show the pathway for the taxonomy staphylococcus(genus) and Kitasatospora(genus), not for staphylococcus aureus (species)

Usage with EC Number
python MacadamExplore.py -tax "staphylococcus aureus,Kitasatospora aureofaciens" -strict true -rank species -prefix Staphy -EC 1.1.1.49
The result file will only show the pathway containing the enzyme 1.1.1.49 (glucose-6-phosphate dehydrogenase (NADP+))

Nitrosotalea devanaterra (Archaea)
python MacadamExplore.py -tax "Nitrosotalea devanaterra" -strict true -rank species -prefix Nitro -func urea

Warning: CyanoBacteria and some Archaea do not have all the taxonomic rank



############## How to use MACADAM with an OTU Table ###########

Each one of your OTU must be link to a taxonomic affiliation showing the seven major taxonomic rank.
Take the taxonomic names your are interested in in your taxonomic affiliation and put it in a python command like the above examples.
Taxonomic names like "Unknown Staphylococcus" are not recognized by MACADAM. You can try "Staphylococcus".

Examples of affiliation:
Bacteria; Firmicutes; Bacilli; Bacillales; Staphylococcaceae; Staphylococcus; Staphylococcus aureus

Example of python command:
  python MacadamExplore.py -tax "staphylococcus aureus" -prefix "Staphy"
Example of python command if you want to check if your OTU is linked to function associated with urea:
  python MacadamExplore.py -tax "staphylococcus aureus" -prefix "Staphy" -func "urea"
MACADAM will check if the taxonomic name exists and if not, check if the genus exists.
If the species is not recognized, you can enter the genus, family, ...



############## Exemple of SQLite command ###########
You can also use SQLite langage to query MACADAM:
First obtain the TaxID link to your taxonomic name:
SELECT taxID from taxonomy where name is "YOUR TAXONOMIC NAME";
Then print all the pathway and associated information corresponding to that taxID
SELECT DISTINCT pathway.taxonomy ,pathway.ID, pathway.strainName, pathway.numberOfPGDBInSpecies, pathway.numberOfPathway, pathway.pathwayScore, pathway.pathwayFrequencyScore, pathway.reasonToKeep, hierarchy.pathwayName from pathway INNER JOIN hierarchy ON (pathway.pathwayFrameID=hierarchy.pathwayFrameID) where taxonomy like "%.YOUR TAXID.%";

Example for all the pathway of Staphylococcus aureus:
SELECT taxID from taxonomy where name is "Staphylococcus aureus";
Output: 1280
SELECT DISTINCT pathway.taxonomy ,pathway.ID, pathway.strainName, pathway.numberOfPGDBInSpecies, pathway.numberOfPathway, pathway.pathwayScore, pathway.pathwayFrequencyScore, pathway.reasonToKeep, hierarchy.pathwayName from pathway INNER JOIN hierarchy ON (pathway.pathwayFrameID=hierarchy.pathwayFrameID) where taxonomy like "%.1280.%";
Output all the pathways associated with it PS and PFS

Warning: SQLITE request do not allow user to see functional information for the upper rank as the python script do.
We advise you to use the python script.

############## Database ###########

MACADAMdatabase.db can be explored:
  - Via command line using the sqlite3 package.
  - Via GUI software compatible with SQLite3, such as SQLite Browser (https://sqlitebrowser.org/)

MACADAM tables (refer to the article and fig 4 for more details):
  - taxonomy: NCBI taxonomy
  - faprotax: FAPROTAX Database
  - IJSEMPhenoDB: IJSEM Phenotypic Database
  - pathway: Metacyc pathways for each organism associated with the completeness score.
  - hierarchy: hierarchy of each pathway
  - MTBName: compound names and MTB-ID
  - RXNMTB: RXN-ID/MTB-ID
  - RXNName:  Reaction Name/RXN-ID
  - ENZName: Enzyme name/ENZ-ID
  - RXNENZ: RXN-ID/ENZ-ID
  - PWYRXN: PWY-ID/RXN-ID
