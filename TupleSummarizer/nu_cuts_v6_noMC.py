
# Import stuff
from ROOT import TH1F
from ROOT import TCanvas
from ROOT import gPad
from ROOT import gROOT
from ROOT import *
import sys
import ROOT
import os
import json
import copy
DEBUG = False
data = True
maxlen = 4
# version 4 switch to TChain from file

# this program reads in a tuple, applies cuts and produces histograms for every variable in the tuple.
# it autocalculates the range using root's algorithm but outputs the ranges so you can use them for consistency or modify them

# arguments are:

# 1 name of list of input root files

# 2 optional - name of txt file (generated by previous run) with fixed ranges for variables.

if len(sys.argv) < 2:
	print (" arguments are ")
  # print (" python nu_cuts_v4.py <input list of root files> [<input limits file>]")
	print (" python nu_cuts_v4.py <input config file>")
  # print (" if no limits file is specified I will make one")
	sys.exit(0)

# map of tags for cuts you might wish to apply

# units are MeV and radians
cuts = {"physical":"RecoName_E<120000",
		"antinu":"RecoName_nuHelicity==2",
		"nu":"RecoName_nuHelicity==1"}   # can implement sets of cuts here
#"recoilEnergy":"recoil_energy_nonmuon_nonvtx100mm<500.",
#"sanity":"abs(CCQENu_minos_trk_p)<120000&&muon_minerva_trk_chi2PerDoF>0",
#"antinu":"CCQENu_nuHelicity==2",
#"muonTheta":"muon_theta<0.4",
#"physical":"CCQENu_E<120000",
#"highpt":"CCQENu_muon_P*sin(muon_theta)>1000",
#"strangeP":"CCQENu_muon_E/mc_primFSLepton[3]>2",
#"goodmu":"CCQENu_minos_trk_eqp_qp<0.4"
#}

# Open and load configuration file
f = open(sys.argv[1])
config = json.load(f)
f.close()

playlist = config["playlist"]
absolutePath = config["absolutePath"]
keepCuts = config["keepCuts"]
recoNames = config["recoNames"]
doData = config["doData"]
doMC = config["doMC"]
samples = []
if doData:
	dataIn = config["dataIn"]
	samples.append("Data")
if doMC:
	dataIn = config["mcIn"]
	samples.append("MC")
cutchoice = config["cutchoice"]

if not absolutePath:
	for name in recoNames:
		dataIn[name] = os.path.join(os.getcwd(),dataIn[name])

#inputlist = open(sys.argv[1],'r').readlines()

newfolder = playlist[0]
for name in recoNames:
	newfolder = newfolder+"_"+name
if not os.path.isdir(newfolder):
	os.mkdir(newfolder)
os.chdir(newfolder)

haslim = {}
rangesname="ranges_"+playlist[0]
for name in recoNames:
	rangesname = rangesname+"_"+name
listing = open(rangesname+".txt",'w')
minimum = {}
maximum = {}
compareConfig = {"recoNames":recoNames}
outputRootFiles = {}

count = {}
histdict = {"Data":{"Shared":[]}}
print("\nReco names are:")
for name in recoNames:
	count[name] = {"Data":0}
	histdict["Data"][name+"_only"] = []
	print("   ",name)
	

for name in recoNames:

	print("\nBegin "+name)

	#thechain = TChain(name)  # root -l file.root ; TBrowser b; # would show you this.
	thechain = TChain(name)
	datalist = open(dataIn[name],'r').readlines()

	#for line in inputlist:
	#  inputfile = line.strip()
	#  thechain.Add(inputfile)

	for line in datalist:
		datafile = line.strip()
		thechain.Add(datafile)

	if (DEBUG):
		thechain.Print()

	TH = "TH1F"

	# set up cuts from the choice you made above

	recoCuts = copy.deepcopy(cuts)
	for c in recoCuts: 
		recoCuts[c] = recoCuts[c].replace("RecoName",name)
		
	thecut = ""
	tag = ""
	print("  The cuts are:")
	for cut in cutchoice:
		thecut += recoCuts[cut] + " && "
		tag +=cut+"_"
		print("   ",cut,"->",recoCuts[cut])
	tag = tag[0:-1]
	thecut = thecut[0:-3]


	##################
	###### DATA ######
	##################

	print("  Begin Data:")

	outname = dataIn[name].replace(".txt","")
	outname = os.path.basename(outname)
	outname = outname+"_"+tag

	if keepCuts:
		cutoutname = "cut_"+outname
		cutfile = TFile(cutoutname+".root",'RECREATE')

	datatuplename = thechain.GetName()

	# inntuple = thechain.Get(tuplename)
	in_data_ntuple = thechain
	if "TChain" not in str(type(thechain)):																														
		print (" no TChain in ",datatuplename)
		sys.exit(1)
	if recoCuts != []:
		print ("    Building smaller tuples with cuts")
		ntuple = in_data_ntuple.CopyTree(thecut)
	else:
		ntuple = thecut
	if keepCuts:
		print("    Cut Data filename:", cutoutname)
		outputRootFiles[name+"_cut"] = cutoutname+".root"

	# make the output histogram
	histoutname = "hist_"+outname
	compareConfig[name] = os.getcwd()+"/"+histoutname+".root"
	outputRootFiles[name+"_hists"] = histoutname+".root"
	houtData = ROOT.TFile(histoutname+".root","RECREATE")
	ROOT.gROOT.SetBatch(True)  # Supresses the drawing canvas
	print("    Data histogram filename:", histoutname,"\n")
	
	data_or_truth_list = []
	for i in ntuple.GetListOfBranches():
		if DEBUG and count[name]["Data"] > 100:
			break

		# figure out if the branch is a variable or an array of variables
		if DEBUG:
			print ("before try", i.GetName())
		if (count[name]["Data"] > -1):
			length = ntuple.GetLeaf(i.GetName()).GetLen()
			branch = i.GetName()
			b = copy.deepcopy(branch)
			if name in branch:
				branch = branch.replace(name,"recoName")
			if DEBUG:
				print (branch)
			if data and "truth" in branch:
				data_or_truth_list.append(branch)
				continue
			
		# if it is a variable, just histogram it.  Ditto if it is huge, then just glom em all together as one.

		if length == 1 or length > maxlen:
			if "_sz" in branch:
				continue
			mini = 0.0
			maxa = 0.0
			count[name]["Data"] = count[name]["Data"]+1
			histdict["Data"][name+"_only"].append(branch)
			if "sz" in branch:
				continue
			# this is some serious root voodoo - use interactive root itself to make a trial histogram to get the ranges into a temporary histogram
			if not branch in haslim:
				ntuple.Draw(b, b + " != - 9999 && "+b+" != - 999")
				htemp = gPad.GetPrimitive("htemp")
				if TH not in str(type(htemp)):
					continue

				mini = htemp.GetBinLowEdge(1)
				maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
				
				minimum[branch] = mini
				maximum[branch] = maxa
				
				htemp.Delete()

				text = "%s %g %g %d\n"%(branch,mini,maxa,length)
				listing.write(text)
				haslim[branch] = True
			else:
			
				mini = minimum[branch]
				maxa = maximum[branch]
				#print(branch+" already has limits: ("+str(mini)+","+str(maxa)+")")

			# now make a histogram with the right range

			htemp = TH1F("htemp",branch,40,mini,maxa)
			htemp.Sumw2()
		    
			if mini == maxa:
				continue
		        
			cut = b+" >= "+str(mini)+" && "+b+" <= "+str(maxa)

			# and fill it

			ntuple.Draw(b+">>htemp",cut)
			#print (cut)

			# and clone it to a real one - this really is voodoo

			real = gPad.GetPrimitive("htemp").Clone()

			if TH not in str(type(real)):
				print (" could not do ",branch)
				continue
			real.SetName(branch)
			real.SetTitle(branch+";"+branch)
			real.Write()
			htemp.Delete()
		else:
			# skip the size branches
			if "_sz" in branch:
				continue
			if name in branch:
				branch = branch.replace(name,"recoName")
				# here if it is a vector - same as the previous
		
			for j in range(0,length):
				nubranch = "%s[%d]"%(branch,j) # "recoName" swap
				nub = "%s[%d]"%(b,j) # Uses original reconame
				branchname = "%s_%d"%(branch,j) # "recoName" swap
				bname = "%s_%d"%(b,j) # Uses original reconame
				mini = 0.0
				maxa = 0.0
				count[name]["Data"] = count[name]["Data"]+1
				histdict["Data"][name+"_only"].append(branchname)
				if not branchname in haslim:
					ntuple.Draw(nub, nub + " != -9999 && "+nub+" != - 999")
					htemp = gPad.GetPrimitive("htemp")
					if TH not in str(type(htemp)):
						continue
		        	
					mini = htemp.GetBinLowEdge(1)
					maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
					
					minimum[branchname] = mini
					maximum[branchname] = maxa
				
					htemp.Delete()
		        	
					text = "%s %g %g %d\n"%(branchname,mini,maxa,length)
					listing.write(text)
					haslim[branchname] = True        
				else:
					mini = minimum[branchname]
					maxa = maximum[branchname]
		          
				htemp = TH1F("htemp",nubranch,40,mini,maxa)
				htemp.Sumw2()
				if DEBUG:
					htemp.Print()
				if mini == maxa:
					continue
				cut = nub+" >= "+str(mini)+" && "+nub+" <= "+str(maxa)
				ntuple.Draw(nub+">>htemp",cut) # loops over all events and histograms them.
				#print (cut)
				real = gPad.GetPrimitive("htemp").Clone()
				if TH not in str(type(real)):
					print (" could not do ",branch)
					continue
				htemp.Delete()
				real.SetName(branchname)
				real.SetTitle(branchname+";"+branchname)
				real.Write()
	#except:
	#  print (" this key failed", i.GetName())
	#  sys.exit(0)
	houtData.Close()
	if keepCuts:
		cutfile.cd()
		ntuple.Write()
		cutfile.Close()
	
	if data:
		histdict["Data"][name+"_no_hist_due_to_truth"] = data_or_truth_list
		print(name+" branches satisfying 'if data and "+'"truth"'+" in branch':")
		for bname in data_or_truth_list:
			print("   "+bname)
	
listing.close()

# Creating JSON file containing list of unique and shared histograms
histdict["Data"]["Shared"] = histdict["Data"][recoNames[0]+"_only"]

for name in recoNames: # Getting shared list
	histdict["Data"]["Shared"] = list(set(histdict["Data"]["Shared"])-(set(histdict["Data"]["Shared"])-set(histdict["Data"][name+"_only"])))
	
for name in recoNames: # Getting unique list for each recoName
	print(name+" total count: "+str(len(histdict["Data"][name+"_only"])))
	histdict["Data"][name+"_only"] = list(set(histdict["Data"][name+"_only"])-set(histdict["Data"]["Shared"]))
	print(name+"_only count: "+str(len(histdict["Data"][name+"_only"])))
print("Shared count: "+str(len(histdict["Data"]["Shared"])))

# Sorting each list alphabetically
histdict["Data"]["Shared"].sort()
for name in recoNames:
	histdict["Data"][name+"_only"].sort()

# Saving to JSON file
json_object = json.dumps(histdict, sort_keys = True, indent = 4)
jname = "histograms_"+playlist[0]+".json"
with open(jname, "w") as outfile:
	outfile.write(json_object)

########

# Saving JSON file listing output root files
json_object = json.dumps(outputRootFiles, indent = 4)
jname = playlist[0]
for name in recoNames:
	jname = jname + "_" + name
jname = jname + "_outputRootFiles.json"
with open(jname, "w") as outfile:
	outfile.write(json_object)

#########

# Saving JSON file listing important paths in HistComp folder
compareFile = os.path.dirname(os.path.dirname(os.getcwd()))
compareConfig["TupleComparisonRoot"] = copy.deepcopy(compareFile)
compareFile = compareFile+"/HistComp/histcompare_"+playlist[0]
for name in recoNames:
	compareFile = compareFile+"_"+name
	
with open(compareFile+".json", "w") as outfile:
    json.dump(compareConfig, outfile, indent = 4)

##########

# Removing unique histrograms from generated hist root files
f = open("histograms_"+playlist[0]+".json","r")
hconfig = json.load(f)
f.close()
for name in recoNames:

	hfile =  TFile.Open(outputRootFiles[name+"_hists"],"update")
	print("Opening "+outputRootFiles[name+'_hists']+" to remove unique histograms")
	keylist = hfile.GetListOfKeys()
	hkeys = {}
	for i in keylist:
		hkeys[i.GetName()]=i.GetCycle()
	for hname in hkeys.keys():
		if hname in hconfig["Data"][name+"_only"]:
			if hkeys[hname] == 1: hfile.Delete(hname+";1")
	hfile.Close()
	
	# For some reason I have to close the file and reopen it to
	# delete the histogram in which cycle = 2
	hfile =  TFile.Open(outputRootFiles[name+"_hists"],"update")
	keylist = hfile.GetListOfKeys()
	hkeys = {}
	for i in keylist:
		hkeys[i.GetName()]=i.GetCycle()
	for hname in hkeys.keys():
		if hname in hconfig["Data"][name+"_only"]:
			if hkeys[hname] == 2: hfile.Delete(hname+";2")
	hfile.Close()
	
#energy_from_mc
#energy_from_mc_fraction
#energy_from_mc_fraction_of_highest
#muon_fuzz_energy
#recoName_r_minos_trk_bdL
#recoName_r_minos_trk_end_dcosz
#recoName_r_minos_trk_vtx_dcosz
#recoName_t_minos_trk_numFSMuons
#recoName_t_minos_trk_primFSLeptonPDG




