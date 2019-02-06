#!/usr/local/bioinfo/src/python/Python-3.4.3/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import argparse
import os, sys, time, zipfile
from collections import defaultdict
import statistics
from operator import itemgetter
import shutil
from collections import Counter


########## arguments ########

#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-verbose",dest="verbose", help="generate full results for debugg in file.results.tsv",default=None)
parser.add_argument("-prefix",dest="prefix", help="random key to name result files",default=None)
parser.add_argument("-tax",dest="tax", help="taxonomy of interest. Carefull with upper case",default=None)
parser.add_argument("-func",dest="func", help="function of interest",default=None)
parser.add_argument("-mtb",dest="mtb", help="metabolite of interest",default=None)
parser.add_argument("-rxn",dest="rxn", help="reaction of interest",default=None)
parser.add_argument("-EC",dest="EC", help="EC Number of interest",default=None)
parser.add_argument("-enz",dest="enz", help="enzyme of interest",default=None)
parser.add_argument("-rank",dest="rank", help="rank of interest if specified",default=None)
parser.add_argument("-min",dest="min", help="minimal score",default=0.0, type=float)
parser.add_argument("-max",dest="max", help="maximal score",default=1.0, type=float)
parser.add_argument("-nonscientific",dest="nonscientific", help="Find Non-scientific Name",default=None)
parser.add_argument("-strict",dest="strict", help="When specified the taxonomy is requested as it is",default="false")
parser = parser.parse_args()

#Tax if for the taxonomy
#func is for a particular function
tax=parser.tax
func=parser.func
rank=parser.rank
MiniScore=parser.min
MaxScore=parser.max
MiniScore=float(MiniScore)
MaxScore=float(MaxScore)
cpd=parser.mtb
rxn=parser.rxn
enz=parser.enz
EC=parser.EC
prefix=parser.prefix
verbose=parser.verbose
nonscientific=parser.nonscientific
strict=parser.strict


lGoodRank=["species","genus","family","order","class","phylum","superkingdom"]
RankofInterest=[]
if rank:
	if rank!="all":
		rank=rank.split(",")
		for element in rank:
			element=element.strip()
			element=element.lower()
			if element in lGoodRank:
				RankofInterest.append(element)
			else:
				print ("Invalid rank. Set to All rank. Rank must be species,genus,family,order,class or phylum. Separator are comas. Check your input")
				sys.exit()
				#RankofInterest=["species","genus","family","order","class","phylum","superkingdom","no rank"]
	else:
		RankofInterest=["all"]
		rank=["all"]
else:
	RankofInterest=["all"]
	rank=["all"]

lTemp=[]
if tax:
	tax=tax.split(",")
	for element in tax:
		element=element.strip()
		element=" ".join(element.split())
		lTemp.append(element)
tax=lTemp

lTemp=[]
if enz:
	enz=enz.split(",")
	for item in enz:
		item=item.strip()
		item=" ".join(item.split())
		item=item.lower()
		lTemp.append(item)
else:
	enz=""
enz=lTemp

lTemp=[]
if cpd:
	cpd=cpd.split(",")
	for item in cpd:
		item=item.strip()
		item=" ".join(item.split())
		item=item.lower()
		lTemp.append(item)
else:
	cpd=""
cpd=lTemp

lTemp=[]
if rxn:
	rxn=rxn.split(",")
	for item in rxn:
		item=item.strip()
		item=" ".join(item.split())
		item=item.lower()
		lTemp.append(item)
else:
	rxn=""
rxn=lTemp

lTemp=[]
if EC:
	EC=EC.split(",")
	for item in EC:
		item=item.strip()
		item=" ".join(item.split())
		item=item.lower()
		lTemp.append(item)
else:
	EC=""
EC=lTemp


lTemp=[]
if func:
	func=func.split(",")
	for item in func:
		item=item.strip()
		item=" ".join(item.split())
		item=item.lower()
		lTemp.append(item)
else:
	func=""

func=lTemp
funcrequest=lTemp


######### function ###############

#Connection to the DB
def Connection_to_DB(db_file):
	#connect to the db and place the cursor
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)

	return None


badtax=[]
bGenus=False
def request_a_taxonomy(tax,dbToolsCursor,RankofInterest):
	#### Store un global variable #####
	global badtax
	global bGenus
	if strict=="true":
		lTemp=[]
		for element in tax:
			lTemp.append(element.capitalize())
		tax=lTemp
		sLikeoption="(name LIKE \""+"\" OR name LIKE \"".join(tax)+"\")"
	else:
		sLikeoption="(name LIKE \"%"+"%\" OR name LIKE \"%".join(tax)+"%\")"
	# tax="\"%"+tax+"%\""
	lListofInputLine=[]
	if RankofInterest==['all']:
	#Find a taxonomy in the Taxonomy table and generate the lineage.
	#Check if tax exist in our database
		lInputLines=ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+";")
		if len(lInputLines)>=1:
			for line in lInputLines:
				lListofInputLine.append(line)
			if lListofInputLine:
				lmatch=[]
				for item in lListofInputLine:
					lmatch.append(item[1])
				for item in tax:
					iNotrecognized=0
					for element in lmatch:
						if item in element:
							iNotrecognized=1
							#print (item+": Exists in our Database")
					if iNotrecognized==0:
						#print (item+": Doesn't exists in our database")
						badtax.append(item)
				return lListofInputLine
		else:
			print (" / ".join(tax)+": Doesn't exists in our database")
			print ("You may consider check your input of the script. Separator are comas")
			print ("Stopping the script")
			lListofInputLine=False

			return lListofInputLine

	else:
		sRankoption="(taxonomicRank IS \""+"\" OR taxonomicRank IS \"".join(RankofInterest)+"\")"
		lInputLines=ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+" AND "+sRankoption+";")
		if len(lInputLines)>=1:
			for line in lInputLines:
				lListofInputLine.append(line)
			if lListofInputLine:
				lmatch=[]
				for item in lListofInputLine:
					lmatch.append(item[1])
				for item in tax:
					iNotrecognized=0
					for element in lmatch:
						if item.lower() in element.lower():
							iNotrecognized=1
							#print (item+": Exists in our Database")
					if iNotrecognized==0:
						#print (item+": Doesn't exists in our database")
						badtax.append(item)
				return lListofInputLine
		else:
			#### If species not found then try to match with only the genus
			if (RankofInterest==['species'] and strict=="false"):
				lTemp=[]
				for item in tax:
					lTemp.append(item.split(" ")[0])
				lTemp=list((set(lTemp)))
				sLikeoption="(name LIKE \"%"+"%\" OR name LIKE \"%".join(lTemp)+"%\")"
				print ("Species not found in NCBI taxonomy try genus")
				lListofInputLine=[]
				#Find a taxonomy in the Taxonomy table and generate the lineage.
				#Check if tax exist in our database
				lInputLines=ExecuteCommand(dbToolsCursor,"SELECT * FROM taxonomy WHERE "+sLikeoption+"AND taxonomicRank IS \"genus\""+";")
				if len(lInputLines)>=1:
					for line in lInputLines:
						lListofInputLine.append(line)
					if lListofInputLine:
						print (" ".join(lTemp)+": Exists in our Database")
						bGenus=True
						return lListofInputLine
				else:
					print (" / ".join(tax)+": Doesn't exists in our database")
					print ("You may consider check your input of the script. Separator are comas")
					print ("Stopping the script")
					outputfile = open("./Results/"+str(prefix)+"."+"compact.tsv","w")
					outputfile.write("Error during file writing")
					outputfile.close()
					lListofInputLine=False
					return lListofInputLine

			else:
				print (" / ".join(tax)+": Doesn't exists in our database with this rank ("+" / ".join(RankofInterest)+")")
				print ("You may consider check your input of the script and the -strict parameter. Separator are comas")
				lListofInputLine=False
				return lListofInputLine

def ExecuteCommand(conn,command):
	conn.execute(command)
	rows = conn.fetchall()
	lOfLines=[]
	for row in rows:
		lOfLines.append(row)
	return lOfLines

def request_pathway_for_a_taxonomy(lLineageRank,MiniScore,MaxScore,func,Precisefunc):
	count=0
	#Preprocess func
	sLikeoption=""
	if func!=[]:
		sLikeoption="(hierarchy.pathwayName LIKE \"%"+"%\" OR hierarchy.pathwayName LIKE \"%".join(func)
		if Precisefunc==[]:
			sLikeoption=sLikeoption+"%\")"
	if Precisefunc!=[]:
		if func!=[]:
			sLikeoption=sLikeoption+"%\" OR hierarchy.pathwayName IS \""+"\" OR hierarchy.pathwayName IS \"".join(Precisefunc)+"\")"
		else:
			sLikeoption="(hierarchy.pathwayName IS \""+"\" OR hierarchy.pathwayName IS \"".join(Precisefunc)+"\")"
	if sLikeoption=="":
		sLikeoption="(hierarchy.pathwayName LIKE \"%%\")"
	func=func+Precisefunc
	sLikeFaprotax="(pathwayName LIKE \"%"+"%\" OR pathwayName LIKE \"%".join(func)+"%\")"
	sLikeIJSEM="(pathway LIKE \"%"+"%\" OR pathway LIKE \"%".join(func)+"%\")"
	#Find the common ancestor in our database
	#lLineageRank=".".join(str(x) for x in list(reversed(lLineageRank)))+"."
	while count==0:
		if lLineageRank.endswith("NaN."):
			lLineageRank=lLineageRank[:-4]
		else:
			ListofPathway=ExecuteCommand(dbToolsCursor,"SELECT DISTINCT pathway.taxonomy ,pathway.ID, pathway.strainName, pathway.numberOfPGDBInSpecies, pathway.numberOfPathway, pathway.pathwayScore, pathway.pathwayFrequencyScore, pathway.reasonToKeep, hierarchy.pathwayName FROM pathway INNER JOIN hierarchy ON (pathway.pathwayFrameID=hierarchy.pathwayFrameID) WHERE pathwayScore BETWEEN "+str(MiniScore)+" AND "+str(MaxScore)+" AND taxonomy LIKE \""+str(lLineageRank)+"%\" AND "+sLikeoption+";")
			#print ("SELECT DISTINCT pathway.taxonomy ,pathway.ID, pathway.strainName, pathway.numberOfPGDBInSpecies, pathway.numberOfPathway, pathway.pathwayScore, pathway.pathwayFrequencyScore, pathway.reasonToKeep, hierarchy.pathwayName FROM pathway INNER JOIN hierarchy ON (pathway.pathwayFrameID=hierarchy.pathwayFrameID) WHERE pathwayScore BETWEEN "+str(MiniScore)+" AND "+str(MaxScore)+" AND taxonomy LIKE \""+str(lLineageRank)+"%\" AND "+sLikeoption+";")
			ListofFaprotax=ExecuteCommand(dbToolsCursor,"SELECT * FROM faprotax WHERE taxonomy LIKE \""+str(lLineageRank)+"%\" AND "+sLikeFaprotax+";")
			ListofIJSEM=ExecuteCommand(dbToolsCursor,"SELECT * FROM IJSEMPhenoDB WHERE taxonomy LIKE \""+str(lLineageRank)+"%\" AND "+sLikeIJSEM+";")
			if (ListofPathway or ListofFaprotax or ListofIJSEM):
				count=1
				MatchPoint=lLineageRank.split(".")[-2]
				# ~ break
			elif lLineageRank=="2." or lLineageRank=="2157.":
				print ("Function doesn't exist or your score is too strict! Skip to next taxonomy")
				count=1
				MatchPoint=None
				ListofPathway=None
				ListofFaprotax=None
			elif strict=="true":
				print ("No function linked to your taxonomy found")
				count=1
				MatchPoint=None
				ListofPathway=None
				ListofFaprotax=None
			else:
				lLineageRank=".".join(lLineageRank.split(".")[0:-1])
				lLineageRank=".".join(lLineageRank.split(".")[0:-1])+"."
	# if  ListofPathway and ListofFaprotax:
	# 	return ListofPathway,ListofFaprotax,MatchPoint
	if not ListofPathway:
		ListofPathway=[]
	if not ListofFaprotax:
		ListofFaprotax=[]
	if not ListofIJSEM:
		ListofIJSEM=[]
	return ListofPathway,ListofFaprotax,ListofIJSEM,MatchPoint
######### Script ################

#Connect the DB and put the cursor
dbTools=Connection_to_DB("/dev/shm/MACADAM/MACADAMdatabase.db")
dbToolsCursor=dbTools.cursor()

##### Find metabolite,rxn and enz name and convert it to pathway.

lListofPWYCPD=[]
lListofCPD=[]
dCPDtoPWY={}
if cpd:
	for element in cpd:
		element=element.strip()
		element=element.lower()
		lListofCPD.extend(ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNMTB ON PWYRXN.RXN = RXNMTB.RXN INNER JOIN MTBName ON RXNMTB.MTB = MTBName.MTB WHERE MTBName.Name LIKE \"%"+element+"%\";"))
		TempTuples=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNMTB ON PWYRXN.RXN = RXNMTB.RXN INNER JOIN MTBName ON RXNMTB.MTB = MTBName.MTB WHERE MTBName.Name LIKE \"%"+element+"%\";")
		TempTuples=[i[0] for i in TempTuples]
		dCPDtoPWY[element]=TempTuples
	for element in lListofCPD:
		for item in element:
			lListofPWYCPD.append(item)

lListofPWYRXN=[]
lListofRXN=[]
dRXNtoPWY={}
if rxn:
	for element in rxn:
		element=element.strip()
		element=element.lower()
		lListofRXN.extend(ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNName ON PWYRXN.RXN = RXNName.RXN WHERE RXNName.Name LIKE \"%"+element+"%\";"))
		TempTuples=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNName ON PWYRXN.RXN = RXNName.RXN WHERE RXNName.Name LIKE \"%"+element+"%\";")
		TempTuples=[i[0] for i in TempTuples]
		dRXNtoPWY[element]=TempTuples
	for element in lListofRXN:
		for item in element:
			lListofPWYRXN.append(item)

lListofPWYENZ=[]
lListofENZ=[]
dENZtoPWY={}
if enz:
	for element in enz:
		element=element.strip()
		element=element.lower()
		lListofENZ.extend(ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNENZ ON PWYRXN.RXN = RXNENZ.RXN INNER JOIN ENZName ON RXNENZ.ENZ = ENZName.ENZ WHERE ENZName.Name LIKE \"%"+element+"%\";"))
		TempTuples=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNENZ ON PWYRXN.RXN = RXNENZ.RXN INNER JOIN ENZName ON RXNENZ.ENZ = ENZName.ENZ WHERE ENZName.Name LIKE \"%"+element+"%\";")
		TempTuples=[i[0] for i in TempTuples]
		dENZtoPWY[element]=TempTuples
	for element in lListofENZ:
		for item in element:
			lListofPWYENZ.append(item)

lListofPWYEC=[]
lListofEC=[]
dECtoPWY={}
if EC:
	for element in EC:
		element=element.strip()
		element=element.lower()
		lListofEC.extend(ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNECNumber ON PWYRXN.RXN = RXNECNumber.RXN WHERE RXNECNumber.ECNumber IS \""+element+"\";"))
		TempTuples=ExecuteCommand(dbToolsCursor,"SELECT distinct(pathwayName) from hierarchy INNER JOIN pathway on hierarchy.pathwayFrameID = pathway.pathwayFrameID INNER JOIN PWYRXN on pathway.pathwayFrameID = PWYRXN.PWY INNER JOIN RXNECNumber ON PWYRXN.RXN = RXNECNumber.RXN WHERE RXNECNumber.ECNumber IS \""+element+"\";")
		TempTuples=[i[0] for i in TempTuples]
		dECtoPWY[element]=TempTuples
	for element in lListofEC:
		for item in element:
			lListofPWYEC.append(item)

Precisefunc=list(set(lListofPWYCPD+lListofPWYRXN+lListofPWYENZ+lListofPWYEC))
func=list(set(func))

if cpd or enz or rxn or EC:
	if not func and not Precisefunc:
		print ("No corresponding name with function name, compounds, enzyme or reactions inputed. Stopping the script")
		outputfile = open("./Results/"+str(prefix)+"."+"compact.tsv","w")
		outputfile.write("No corresponding name with function name, compounds, enzyme or reactions inputed")
		func=False
		outputfile.close()

StricttooStrict=0

if func!=False:
	try:
		if tax :
			#request the taxIDs for a string
			lLineofInterest=request_a_taxonomy(tax,dbToolsCursor,RankofInterest)
			#Check if lLineofInterest is false to exit to the next loop
			if lLineofInterest:
				#Keep Only scientific name
				lTemp=[]
				for line in lLineofInterest:
					if line[2]=='scientific name':
						lTemp.append(line)
					if nonscientific:
						print ("Warning you do not enter the scientific name for the species: "+line[1]+" which is a "+line[2])
						print ("This can cause problem on the results file")
						print ("Continuing anyway")
						lMissTax=[line[1],line[2]]
						sNonScientificName=1
						lTemp.append(line)
					else:
						sNonScientificName=False
				lLineofInterest=lTemp

				setOfAllLineage=set()
				dTaxIDtoLineage={}
				dLineofInterest={}
				for line in lLineofInterest:
					dLineofInterest[line[0]]=line[1]
					setOfAllLineage.add(line[5])
					dTaxIDtoLineage[line[0]]=line[5]

				dLineagetoPathway={}
				dLineagetoFaprotax={}
				dLineagetoIJSEM={}
				dLineageToMatchingPoint={}

				for item in setOfAllLineage:
					ListofResults=request_pathway_for_a_taxonomy(item,MiniScore,MaxScore,func,Precisefunc)
					if (ListofResults[0] or ListofResults[1] or ListofResults[2]):
						print ("Pathway found for this lineage: "+item+" !")
						dLineagetoPathway[item]=ListofResults[0]
						dLineagetoFaprotax[item]=ListofResults[1]
						dLineagetoIJSEM[item]=ListofResults[2]
						dLineageToMatchingPoint[item]=ListofResults[3]
					else:
						print ("No results. Check your -strict parameters")
						StricttooStrict=1
						dTaxIDtoLineage.pop(int(item.split(".")[-2]))
						badtax.append(int(item.split(".")[-2]))
						# break
				for key in dLineagetoPathway:
					if len(dLineagetoPathway[key])==0:
						ListofPathway=["None"]
				for key in dLineagetoFaprotax:
					if len(dLineagetoFaprotax[key])==0:
						ListofFaprotax=["None"]
				for key in dLineagetoIJSEM:
					if len(dLineagetoIJSEM[key])==0:
						ListofIJSEM=["None"]

				lAllPathway=[]
				lAllTaxIDMatching=[]
				lAllTaxID=[]
				lTaxonomyMatching=[]
				lTaxonomy=[]
				dTaxIDtoTaxonomy={}
				lAllPathwayFaprotax=[]
				lAllPathwayIJSEM=[]
				lDebugResults=[]
				#Store organism per pathway
				dPathwaytoStrain={}
				if verbose:
					outputfile = open("./Results/"+str(prefix)+"."+"resultat.tsv","w")
				for key in dTaxIDtoLineage:
					if key!=742887:
						if verbose:
							outputfile.write("##TaxID:"+str(key)+"\n")
						lAllTaxID.append(str(key))
						dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(key)+"\" AND typeOfName IS \"scientific name\"")
						taxonomy = dbToolsCursor.fetchone()
						if verbose:
							outputfile.write("##Taxonomy: "+str(taxonomy[0])+" "+str(taxonomy[1])+"\n")
						lTaxonomy.append(str(taxonomy[0]))
						dTaxIDtoTaxonomy[key]=taxonomy[0]
						if verbose:
							outputfile.write("##Matching Point of the Database: "+str(dLineageToMatchingPoint[dTaxIDtoLineage[key]])+"\n")
						lAllTaxIDMatching.append(str(dLineageToMatchingPoint[dTaxIDtoLineage[key]]))
						dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(dLineageToMatchingPoint[dTaxIDtoLineage[key]])+"\" AND typeOfName IS \"scientific name\"")
						taxonomy = dbToolsCursor.fetchone()
						if verbose:
							outputfile.write("##Matching Point Taxonomy: "+str(taxonomy[0])+" "+str(taxonomy[1])+"\n")
						lTaxonomyMatching.append(str(taxonomy[0]))
						if dLineagetoPathway[dTaxIDtoLineage[key]]!=[]:
							if verbose:
								outputfile.write("\n#MetaCyc & MicroCyc:\n")
							for item in dLineagetoPathway[dTaxIDtoLineage[key]]:
								if item[-1] in dPathwaytoStrain:
									dPathwaytoStrain[item[-1]].append(item[2])
								else:
									dPathwaytoStrain[item[-1]]=[item[2]]
								if verbose:
									outputfile.write("\t".join(str(x) for x in item))
									outputfile.write("\n")
								lAllPathway.append([item,key])
						if dLineagetoFaprotax[dTaxIDtoLineage[key]]!=[]:
							if verbose:
								outputfile.write("\n\n#Faprotax:\n")
							for item in dLineagetoFaprotax[dTaxIDtoLineage[key]]:
								dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(item[1])+"\" AND typeOfName IS \"scientific name\"")
								taxonomy = dbToolsCursor.fetchone()
								lAllPathwayFaprotax.append([item,key])
								if verbose:
									outputfile.write(str(item[0])+"\t"+str(taxonomy[0])+" "+str(taxonomy[1])+"\t"+str(item[2])+"\t")
									outputfile.write("\n")
						if dLineagetoIJSEM[dTaxIDtoLineage[key]]!=[]:
							if verbose:
								outputfile.write("\n\n#Faprotax:\n")
							for item in dLineagetoIJSEM[dTaxIDtoLineage[key]]:
								dbToolsCursor.execute("SELECT name,taxonomicRank FROM taxonomy WHERE taxID IS \""+str(item[1])+"\" AND typeOfName IS \"scientific name\"")
								taxonomy = dbToolsCursor.fetchone()
								lAllPathwayIJSEM.append([item,key])
								if verbose:
									outputfile.write(str(item[0])+"\t"+str(taxonomy[0])+" "+str(taxonomy[1])+"\t"+str(item[2])+"\t")
									outputfile.write("\n")
				if verbose:
					outputfile.close()
				### for metacyc pathway###
				if lAllPathway!=[]:
					SetOfPathwayPerPGDBs=set()
					CounterOfPathway=[]
					dPathwaysInfo={}
					setOfPresentPathwayName=set()
					setOfPresentLineage=set()
					for item in lAllPathway:
						SetOfPathwayPerPGDBs.add(item[0])
						setOfPresentPathwayName.add(item[0][-1])
						setOfPresentLineage.add(item[0][1])
					for element in SetOfPathwayPerPGDBs:
						CounterOfPathway.append(element[-1])
					CounterOfPathway=Counter(CounterOfPathway)
					dPathwaysInfo=dPathwaysInfo.fromkeys(setOfPresentPathwayName,None)
					iNumberofSpeciesMatch=len(setOfPresentLineage)

					#Store all needed information in the following dictionnary: dPathwaysInfo[pathway name]=[number of organism with this pathway,]
					for item in lAllPathway:
						if dPathwaysInfo[item[0][-1]]:

							dPathwaysInfo[item[0][-1]][0]=CounterOfPathway[item[0][-1]]
							dPathwaysInfo[item[0][-1]][1].append(float(item[0][5]))
							dPathwaysInfo[item[0][-1]][2].append(float(item[0][6]))
							dPathwaysInfo[item[0][-1]][3].append(item[1])

						else:
							dPathwaysInfo[item[0][-1]]=[1,[float(item[0][5])],[float(item[0][6])],[item[1]]]

					for item in dPathwaysInfo:
						dPathwaysInfo[item][1]=statistics.median(dPathwaysInfo[item][1])
						dPathwaysInfo[item][2]=statistics.median(dPathwaysInfo[item][2])
						dPathwaysInfo[item][3]=set(dPathwaysInfo[item][3])

				with open("./Results/"+str(prefix)+"."+"compact.tsv","w")as outputfile:
					if sNonScientificName:
						outputfile.write("##Warning you do not enter the scientific name for the species: "+lMissTax[0]+" which is a "+lMissTax[1]+"\n")
					if bGenus is True:
						outputfile.write("##Species not found, results are shown for Genus. Maybe bad spelling or misused rank/strict parameters? \n")
					outputfile.write("##This result file was processed for the following inputs: taxonomy(ies):"+", ".join(tax))
					if strict=="true":
						outputfile.write(", with a strict query")
					outputfile.write(", on rank(s):"+", ".join(rank)+", with a maximal completeness score of "+str(MaxScore)+", with a minimal completeness score of "+str(MiniScore))
					if cpd:
						outputfile.write(", on metabolite(s): "+", ".join(cpd))
					if rxn:
						outputfile.write(", on reaction(s): "+", ".join(rxn))
					if enz:
						outputfile.write(", with enzyme(s): "+", ".join(enz))
					if EC:
						outputfile.write(", with EC Number(s): "+", ".join(EC))
					if funcrequest:
						outputfile.write(" and with function(s) containing: "+", ".join(funcrequest))
					outputfile.write("\n")
					if badtax:
						lLineBadtax=[]
						lLineStricttax=[]
						for element in badtax:
							if type(element) is int:
								lLineStricttax.append(dLineofInterest[element].lower().capitalize())
							else:
								lLineBadtax.append(element.lower().capitalize())
						dLineBadtax={v.lower(): v for v in lLineStricttax}.values()

						for element in dLineBadtax:
							lLineStricttax.append(element)
						if lLineBadtax:
							for element in lLineBadtax:
								outputfile.write("##This taxonomy input has not been recognized: "+element+". The result file do not contain any results from this taxonomy. Check your input.\n")
						if lLineStricttax:
							for element in set(lLineStricttax):
								outputfile.write("##This taxonomy input has been recognized: "+element+" but no linked functional information in MACADAM Database. To obtain functional information on a upper rank of its lineage, select \"no strict taxonomy\" on the main page for more results\n")
					for element in lAllTaxID:
						indexlist=lAllTaxID.index(element)
						if lTaxonomy[indexlist]==lTaxonomyMatching[indexlist]:
							outputfile.write("##The requested taxonomy (TaxID: "+lAllTaxID[indexlist]+", Taxonomy: "+lTaxonomy[indexlist]+") is linked to functional information in MACADAM Database\n")
							outputfile.write("##NCBI Taxonomy link: https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+lAllTaxID[indexlist]+"&lin=s\n")
						else:
							TempRank=ExecuteCommand(dbToolsCursor,"SELECT taxonomicRank from taxonomy where taxID is \""+lAllTaxIDMatching[indexlist]+"\";")
							outputfile.write("##The requested taxonomy  (TaxID: "+lAllTaxID[indexlist]+", Taxonomy: "+lTaxonomy[indexlist]+") is not linked to functional information in MACADAM Database but the functional information for a upper rank of its lineage is displayed: "+lAllTaxIDMatching[indexlist]+", Taxonomy: "+lTaxonomyMatching[indexlist]+" ("+TempRank[0][0]+")\n")
							outputfile.write("##NCBI Taxonomy link: https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+lAllTaxIDMatching[indexlist]+"&lin=s\n")
					if lAllPathway!=[]:
						outputfile.write("\n##Functional information from MetaCyc & MicroCyc:\n")
						outputfile.write("Metabolic Pathway\tPresent in X org./Total org.\tMedian of score\tMedian of frequency\tMetabolite\tReaction\tEnzyme\tEC Number\tTarget taxonomies\tStrain with the Pathway\tPathway Hierarchy\tMetaCyc URL\n")
						with open("./Results/"+prefix+".MetaCyc.json","w") as outputjson:
							LStoreJSON=[]
							LStoreJSON.append("{\"data\":[")
							ListofMetacyctowrite=[]
							for item in dPathwaysInfo:
								dbToolsCursor.execute("SELECT PathwayHierarchy from hierarchy where pathwayName is \""+item+"\";")
								hierarchy=dbToolsCursor.fetchall()
								hierarchy=[i for sub in hierarchy for i in sub]
								hierarchy="/".join(hierarchy)
								hierarchy=hierarchy.replace("Pathways.","")
								BeginningofLine=[item,str(dPathwaysInfo[item][0])+"/"+str(iNumberofSpeciesMatch),str(round(dPathwaysInfo[item][1],2)),str(round(dPathwaysInfo[item][2],2))]
								lTemp=""
								if item in lListofPWYCPD:
									for piece in dCPDtoPWY:
										for thing in dCPDtoPWY[piece]:
											if item==thing:
												lTemp=lTemp+piece+" "
									lTemp=lTemp+"\t"
								else:
									lTemp="NA\t"
								if item in lListofPWYRXN:
									for piece in dRXNtoPWY:
										for thing in dRXNtoPWY[piece]:
											if item==thing:
												lTemp=lTemp+piece+" "
									lTemp=lTemp+"\t"
								else:
									lTemp=lTemp+"NA\t"
								if item in lListofPWYENZ:
									for piece in dENZtoPWY:
										for thing in dENZtoPWY[piece]:
											if item==thing:
												lTemp=lTemp+piece+" "
									lTemp=lTemp+"\t"
								else:
									lTemp=lTemp+"NA\t"
								if item in lListofPWYEC:
									for piece in dECtoPWY:
										for thing in dECtoPWY[piece]:
											if item==thing:
												lTemp=lTemp+piece+" "
								else:
									lTemp=lTemp+"NA"
								BeginningofLine.append(lTemp)
								lTemp=[]
								for element in dPathwaysInfo[item][3]:
									lTemp.append(dTaxIDtoTaxonomy[element])
								StrainOfInterest=dPathwaytoStrain[item]
								StrainOfInterest=", ".join(StrainOfInterest)
								EndofLine=[", ".join(lTemp),hierarchy]
								EndofLine.append(StrainOfInterest)
								EndofLine[1],EndofLine[2]=EndofLine[2],EndofLine[1]
								try:
									URLMetacyc=["https://metacyc.org/META/new-image?type=PATHWAY&object="+hierarchy.split(".")[-2]+"\n"]
								except:
									URLMetacyc=["https://metacyc.org/META/new-image?type=PATHWAY&object="+hierarchy.split(".")[-1]+"\n"]

								LinetoWrite=BeginningofLine+EndofLine+URLMetacyc
								ListofMetacyctowrite.append(LinetoWrite)
							ListofMetacyctowrite=sorted(ListofMetacyctowrite,key=itemgetter(5))
							for item in ListofMetacyctowrite:
								outputfile.write("\t".join(item))
								item[4]=item[4].replace("\t","\",\"")
								item[-1]=item[-1].replace("\n","")
								LStoreJSON.append("[\""+"\",\"".join(item)+"\"],")
							LStoreJSON[-1]=LStoreJSON[-1][:-1]
							LStoreJSON.append("]}")
							outputjson.write("".join(LStoreJSON))

				#### For Faprotax ####
				if lAllPathwayFaprotax!=[]:
					dPathwaysInfo={}
					setOfPresentPathwayName=set()
					setOfPresentLineage=set()
					for item in lAllPathwayFaprotax:
						setOfPresentPathwayName.add(item[0][-1])
						setOfPresentLineage.add(item[0][1])

					dPathwaysInfo=dPathwaysInfo.fromkeys(setOfPresentPathwayName,None)
					iNumberofSpeciesMatch=len(setOfPresentLineage)

					for item in lAllPathwayFaprotax:
						if dPathwaysInfo[item[0][-1]]:
							dPathwaysInfo[item[0][-1]][0]+=1
							dPathwaysInfo[item[0][-1]][1].append(item[1])
						else:
							dPathwaysInfo[item[0][-1]]=[1,[item[1]]]

					with open("./Results/"+str(prefix)+"."+"compact.tsv","a")as outputfile:
						outputfile.write("\n##Functional information from Faprotax:\n")
						outputfile.write("Functional feature\tPresent in X org./Total org.\tTarget Taxonomies\n")
						with open("./Results/"+prefix+".Faprotax.json","w") as outputjson:
							LStoreJSON=[]
							LStoreJSON.append("{\"data\":[")
							for item in sorted(dPathwaysInfo):
								outputfile.write(item+"\t"+str(round(dPathwaysInfo[item][0],2))+"/"+str(iNumberofSpeciesMatch)+"\t")
								lTemp=[]
								for itemitem in dPathwaysInfo[item][1]:
									lTemp.append(dTaxIDtoTaxonomy[itemitem])
								lTemp=list(set(lTemp))
								outputfile.write(", ".join(lTemp)+"\n")
								LStoreJSON.append("[\""+item+"\",\""+str(round(dPathwaysInfo[item][0],2))+"/"+str(iNumberofSpeciesMatch)+"\",\""+", ".join(lTemp)+"\"],")
							LStoreJSON[-1]=LStoreJSON[-1][:-1]
							LStoreJSON.append("]}")
							outputjson.write("".join(LStoreJSON))

				#### For IJSEM ####
				if lAllPathwayIJSEM!=[]:
					dPathwaysInfo={}
					setOfPresentPathwayName=set()
					setOfPresentLineage=set()
					for item in lAllPathwayIJSEM:
						#Some organism in IJSEM do not contain any functionnal information
						if item[0][3]!='':
							setOfPresentPathwayName.add(item[0][3])
							setOfPresentLineage.add(item[0][1])

					dPathwaysInfo=dPathwaysInfo.fromkeys(setOfPresentPathwayName,None)
					iNumberofSpeciesMatch=len(setOfPresentLineage)

					for item in lAllPathwayIJSEM:
						if item[0][3]!='':
							if dPathwaysInfo[item[0][3]]:
								dPathwaysInfo[item[0][3]][0]+=1
								dPathwaysInfo[item[0][3]][1].append(item[1])
							else:
								dPathwaysInfo[item[0][3]]=[1,[item[1]]]

					with open("./Results/"+str(prefix)+"."+"compact.tsv","a")as outputfile:
						outputfile.write("\n##Functional information from IJSEM phenotypic database:\n")
						outputfile.write("Functional feature\tPresent in X org./Total org.\tTarget Taxonomies\n")
						with open("./Results/"+prefix+".IJSEM.json","w") as outputjson:
							LStoreJSON=[]
							LStoreJSON.append("{\"data\":[")
							for item in sorted(dPathwaysInfo):
								outputfile.write(item+"\t"+str(round(dPathwaysInfo[item][0],2))+"/"+str(iNumberofSpeciesMatch)+"\t")
								lTemp=[]
								for itemitem in dPathwaysInfo[item][1]:
									lTemp.append(dTaxIDtoTaxonomy[itemitem])
								lTemp=list(set(lTemp))
								outputfile.write(", ".join(lTemp)+"\n")
								LStoreJSON.append("[\""+item+"\",\""+str(round(dPathwaysInfo[item][0],2))+"/"+str(iNumberofSpeciesMatch)+"\",\""+", ".join(lTemp)+"\"],")
							LStoreJSON[-1]=LStoreJSON[-1][:-1]
							LStoreJSON.append("]}")
							outputjson.write("".join(LStoreJSON))

			else:
				outputfile = open("./Results/"+str(prefix)+"."+"compact.tsv","w")
				outputfile.write("Taxonomy not found, doesn't exit exist in NCBI taxonomy or with wrong rank. Check your input or the -strict parameter")
				outputfile.close()
	except:
		outputfile = open("./Results/"+str(prefix)+"."+"compact.tsv","w")
		if StricttooStrict==1:
			outputfile.write("Your usage of the -strict true parameter limits the result. MACADAM doesn't have any functional information for the taxonomy requested and cannot go to a upper rank with the -strict parameter.")
		else:
			outputfile.write("Error during file writing. Check if your taxonomic input. You can use the NCBI website to check that your input exist (https://www.ncbi.nlm.nih.gov/taxonomy)")

		outputfile.close()

f = zipfile.ZipFile("./Results/"+str(prefix)+"."+"tsv.zip",'w',zipfile.ZIP_DEFLATED)
f.write("./Results/"+str(prefix)+"."+"compact.tsv")
f.close()
