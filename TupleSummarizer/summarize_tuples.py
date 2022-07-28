
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

# The only argument is the input configuration file

if len(sys.argv) < 2:
	print ("\nInput should be of the form:\n")
	print ("   python summarize_tuples.py <input config file>\n")
	sys.exit(1)
elif len(sys.argv) >= 2:
	if sys.argv[1][-5:] != ".json":
		print('\nInput configuration file should be a JSON file, i.e. ending in ".json".\n')
		sys.exit(1)
	elif not os.path.exists(sys.argv[1]):
		print("\nInput configuration file "+sys.argv[1]+" does not seem to exist. Check spelling or path.\n")
		sys.exit(1)
if len(sys.argv) >= 3:
	item = sys.argv[2]
	if item == "DEBUG" or item == "debug" or item == "Debug":
		DEBUG = True
	else:
		print("\nUnable to interpet 2nd argument. Should be 'DEBUG' or something.\n")

TH = "TH1F"

# Open and load configuration file. Extract contents.
config = json.load(open(sys.argv[1],"r"))

playlist = config["playlist"]
reconames = config["reconames"]
samples = config["samples"]
cutchoice = config["cutchoice"]
keepcuts = config["keepcuts"]
dropUniqueHists = config["drop_unique_hists"]
hasranges = config["hasranges"]
# Open cuts dictionary. Units are MeV and radians probably (see "README" in cuts dictionary).
cuts = json.load(open(config["cuts_dictionary"],"r"))["cuts"]

# Load ranges if applicable. Initialize branch/histogram limits tracker.
minimum = {}
maximum = {}
length = {}
if hasranges and branch in minimum:
	ranges = json.load(open(config["rangefile"],"r"))
		
# Output range file will be generated regardless of input one or not.
# Create output file names and folder name
output_folder = playlist
for sample in samples:
	output_folder += "_"+sample
for name in reconames:
	output_folder += "_"+name
for cut in cutchoice:
	output_folder += "_"+cut
output_summary_file = "summary.json"
output_range_file = "ranges.json"
output_histdict_file = "histdirectory.json"
output_HistComp_file = "config_HistComp.json"
output_playlist_file = "playlistfiles.json"

# Create (if necessary) and enter output folder and create histcomp folder
output_HistComp_folder = os.path.dirname(os.getcwd())+"/HistComp/"+output_folder
if not os.path.isdir(output_HistComp_folder):
	os.mkdir(output_HistComp_folder)

if not os.path.isdir(output_folder):
	os.mkdir(output_folder)
os.chdir(output_folder)

# Initialize output configuration files, fill where possible
summary = {
           "folder_path":os.getcwd(),
           "input_config": sys.argv[1],
           "playlist": playlist,
           "playlist_files":output_playlist_file,
           "reconames": reconames,
           "samples": samples,
           "output_range_file":output_range_file,
           "cuts": {},
           "histogram_directory":output_histdict_file,
           "histcomp_folder_path":output_HistComp_folder,
           "config_HistComp":output_HistComp_file,
           "histograms": {}
          }
for cut in cutchoice: summary["cuts"][cut] = cuts[cut]
if keepcuts: summary["passed_cuts"] = {}

histdict = {
            "shared": [],
            "ignored": {
                        "not_shared": {},
                        "sz_branch": {},
                        "not_TH": {}
                       }
           }
if data: histdict["ignored"]["truth"] = {}

hist_count = {}
temp_histdict = {}
playlist_files = {}

HistComp_config = {
                   "summary": os.getcwd()+"/"+output_summary_file,
                   "compare_reconames": True,
                   "compare_samples": False
                  }

for sample in samples:
	for name in reconames:		
		summary["histograms"][sample+"_"+name] = "hist_"+name+"_"+sample+".root"
		if keepcuts: summary["passed_cuts"][sample+"_"+name] = "cuts_"+name+"_"+sample+".root"
		histdict["ignored"]["not_shared"][sample+"_"+name] = []
		histdict["ignored"]["sz_branch"][sample+"_"+name] = []
		histdict["ignored"]["not_TH"][sample+"_"+name] = {}
		if data: histdict["ignored"]["truth"][sample+"_"+name] = []
		
		hist_count[sample+"_"+name] = 0
		temp_histdict[sample+"_"+name] = []
		playlist_files[sample+"_"+name] = []

samples_list = "["
names_list = "["
for sample in samples: samples_list += sample+","
for name in reconames: names_list += name+","
samples_list = samples_list[0:-1]+"]"
names_list = names_list[0:-1]+"]"

print("\nSamples are: "+samples_list)
print("Reco names are: "+names_list)

for sample in samples:
	print("\nBegin "+sample+":")
	linebreak = False
	for name in reconames:
		if linebreak:
			print("\n   Begin "+name+":")
		else: 
			print("   Begin "+name+":")
			linebreak = True
		
		# Set up cuts 
		thecut = ""
		recoCuts = copy.deepcopy(summary["cuts"])
		maxcutnamelength = 0
		for cut in cutchoice: 
			recoCuts[cut] = recoCuts[cut].replace("recoName",name)
			thecut += recoCuts[cut] + " && "
			maxcutnamelength = max(len(cut),maxcutnamelength)
		thecut = thecut[0:-4]

		# Print implemented cuts
		print("      The chosen cuts are:")
		for cut in cutchoice:
			spaces = ""
			for i in range(maxcutnamelength - len(cut)): spaces += " "
			print("         "+cut+spaces+" : "+recoCuts[cut])

		#thechain = TChain(name)  # root -l file.root ; TBrowser b; # would show you this.
		thechain = TChain(name)
		input_file_list = open(config[sample][name],'r').readlines()

		for line in input_file_list:
			input_file = line.strip()
			playlist_files[sample+"_"+name].append(input_file)
			thechain.Add(input_file)

		if (DEBUG):
			thechain.Print()

		if keepcuts:
			cfilepath = summary["passed_cuts"][sample+"_"+name]
			cfilename = os.path.basename(cfilepath)
			cutfile = TFile(cfilename,'RECREATE')

		tuplename = thechain.GetName()

		# inntuple = thechain.Get(tuplename)
		in_ntuple = thechain
		if "TChain" not in str(type(thechain)):																														
			print ("      No TChain in "+tuplename)
			sys.exit(1)
		if recoCuts != []:
			print ("\n      Building smaller tuples with cuts")
			ntuple = in_ntuple.CopyTree(thecut)
		else:
			ntuple = thecut
		if keepcuts:
			print("      Cut Data filename: "+cfilename)

		# make the output histogram
		hfilepath = summary["histograms"][sample+"_"+name]
		hfilename = os.path.basename(hfilepath)
		houtData = ROOT.TFile(hfilename,"RECREATE")
		ROOT.gROOT.SetBatch(True)  # Supresses the drawing canvas
		print("      "+sample+" "+name+" histogram filename: "+hfilename+"\n")
		
		data_and_truth_list = []
		not_TH = {}
		for i in ntuple.GetListOfBranches():
			if DEBUG and hist_count[sample+"_"+name] > 100:
				break
			if len(i.GetName()) == 0:
				continue

			# Figure out if the branch is a variable or an array of variables
			if DEBUG:
				print("Before trying "+i.GetName())
			if (hist_count[sample+"_"+name] > -1):
				branch = i.GetName()
				anatool_branch = copy.deepcopy(branch)
				if name in branch:
					branch = branch.replace(name,"recoName")
				if data and "truth" in branch:
					data_and_truth_list.append(branch)
					continue
				branchLength = ntuple.GetLeaf(i.GetName()).GetLen()
				
			# if it is a variable, just histogram it.  Ditto if it is huge, then just glom em all together as one.

			if branchLength == 1 or branchLength > maxlen:
				if "_sz" in branch:
					histdict["ignored"]["sz_branch"][sample+"_"+name].append(branch)
					continue
				if "sz" in branch:
					histdict["ignored"]["sz_branch"][sample+"_"+name].append(branch)
					continue
				mini = 0.0
				maxa = 0.0
				# Here is some root voodoo - use interactive root itself to make a trial histogram to get the ranges into a temporary histogram
				if hasranges and branch in ranges:
					minimum[branch] = ranges[branch][0]
					maximum[branch] = ranges[branch][1]
					mini = minimum[branch]
					maxa = maximum[branch]
				elif branch in minimum:
					mini = minimum[branch]
					maxa = maximum[branch]
				else:
					ntuple.Draw(anatool_branch,anatool_branch+" != - 9999 && "+anatool_branch+" != - 999")
					htemp = gPad.GetPrimitive("htemp")
					if TH not in str(type(htemp)):
						not_TH[branch] = str(type(htemp))
						continue
					mini = htemp.GetBinLowEdge(1)
					maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
					minimum[branch] = copy.deepcopy(mini)
					maximum[branch] = copy.deepcopy(maxa)
					htemp.Delete()
					
				temp_histdict[sample+"_"+name].append(branch)
				length[branch] = copy.deepcopy(branchLength)
				hist_count[sample+"_"+name] = hist_count[sample+"_"+name]+1
				
				# Make a histogram with the correct range
				htemp = TH1F("htemp",branch,40,mini,maxa)
				htemp.Sumw2()
				if mini == maxa: 
					continue
				cut = anatool_branch+" >= "+str(mini)+" && "+anatool_branch+" <= "+str(maxa)
				# Fill it
				ntuple.Draw(anatool_branch+">>htemp",cut)
				# Clone it to a real one - this really is voodoo
				real = gPad.GetPrimitive("htemp").Clone()

				if TH not in str(type(real)):
					not_TH[anatool_branch] = str(type(real))
					continue
				real.SetName(branch)
				real.SetTitle(branch+";"+branch)
				real.Write()
				htemp.Delete()
			else:
				# Skip the size branches
				if "_sz" in branch:
					histdict["ignored"]["sz_branch"][sample+"_"+name].append(branch)
					continue
				if name in branch:
					branch = branch.replace(name,"recoName")
					# Here if it is a vector - same as the previous
			
				for j in range(0,branchLength):
					nubranch_n = "%s[%d]"%(branch,j) # "recoName" swap
					anatool_nubranch_n = "%s[%d]"%(anatool_branch,j) # Uses original reconame
					branch_n = "%s_%d"%(branch,j) # "recoName" swap
					anatool_branch_n = "%s_%d"%(anatool_branch,j) # Uses original reconame
					mini = 0.0
					maxa = 0.0
					
					if hasranges and branch_n in ranges:
						minimum[branch_n] = copy.deepcopy(ranges[branch_n][0])
						maximum[branch_n] = copy.deepcopy(ranges[branch_n][1])
						mini = minimum[branch_n]
						maxa = maximum[branch_n]
					elif branch_n in minimum:
						mini = minimum[branch_n]
						maxa = maximum[branch_n]
					else:
						ntuple.Draw(anatool_nubranch_n,anatool_nubranch_n+" != -9999 && "+anatool_nubranch_n+" != - 999")
						htemp = gPad.GetPrimitive("htemp")
						if TH not in str(type(htemp)):
							not_TH[anatool_branch_n] = str(type(htemp))
							continue
						mini = htemp.GetBinLowEdge(1)
						maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
						minimum[branch_n] = copy.deepcopy(mini)
						maximum[branch_n] = copy.deepcopy(maxa)
						htemp.Delete()
						
					temp_histdict[sample+"_"+name].append(branch_n)
					length[branch_n] = copy.deepcopy(branchLength)
					hist_count[sample+"_"+name] = hist_count[sample+"_"+name]+1
					
					# Make a histogram with the correct range
					htemp = TH1F("htemp",nubranch_n,40,mini,maxa)
					htemp.Sumw2()
					if DEBUG:
						htemp.Print()
					if mini == maxa:
						continue
					cut = anatool_nubranch_n+" >= "+str(mini)+" && "+anatool_nubranch_n+" <= "+str(maxa)
					# Fill it
					ntuple.Draw(anatool_nubranch_n+">>htemp",cut)
					# Clone it to a real one - this really is voodoo
					real = gPad.GetPrimitive("htemp").Clone()
					if TH not in str(type(real)):
						not_TH[anatool_branch_n] = str(type(real))
						continue
					htemp.Delete()
					real.SetName(branch_n)
					real.SetTitle(branch_n+";"+branch_n)
					real.Write()
		#except:
		#  print (" this key failed "+i.GetName())
		#  sys.exit(1)
		houtData.Close()
		if keepcuts:
			cutfile.cd()
			ntuple.Write()
			cutfile.Close()
		
		if data:
			data_and_truth_list.sort()
			histdict["ignored"]["truth"][sample+"_"+name] = data_and_truth_list
			print("\n      "+name+" "+sample+" branches satisfying 'if data and "+'"truth"'+" in branch':")
			for branch in data_and_truth_list:
				print("         "+branch)
		if len(list(not_TH.keys())) > 0:
			for branch in sorted(not_TH):
				histdict["ignored"]["not_TH"][sample+"_"+name][branch] = not_TH[branch]
			print("\n      "+name+" "+sample+" branches that do not draw a TH* object:")
			longestName = ""
			for branch in sorted(not_TH):
				if len(branch) > len(longestName):
					longestName = branch
			for branch in sorted(not_TH):
				spaces = "   "
				for i in range(len(longestName)-len(branch)): spaces += " "
				print("         "+branch+","+spaces+"type: "+not_TH[branch])

# Creating JSON file containing list of unique and shared histograms
print("")
temp_list = []
for sample in samples:
	for name in reconames:
		temp_list.append(temp_histdict[sample+"_"+name])
histdict["shared"] = list(set.intersection(*map(set,temp_list))) # Getting shared list
for sample in samples:
	for name in reconames: # Getting unique list for each recoName
		print(sample+" "+name+" total histogram count: "+str(len(temp_histdict[sample+"_"+name])))
		histdict["ignored"]["not_shared"][sample+"_"+name] = list(set(temp_histdict[sample+"_"+name])-set(histdict["shared"]))
		print("Unshared "+sample+" "+name+" histogram count: "+str(len(histdict["ignored"]["not_shared"][sample+"_"+name])))
print("Shared histogram count: "+str(len(histdict["shared"])))

# Sorting each list alphabetically and creating list for ranges
rangesList = []
histdict["shared"].sort()
for sample in samples:
	for histname in histdict["shared"]:
		rangesList.append(histname)
	for name in reconames:
		histdict["ignored"]["not_shared"][sample+"_"+name].sort()
		histdict["ignored"]["sz_branch"][sample+"_"+name].sort()
		if data: histdict["ignored"]["truth"][sample+"_"+name]
		histdict["ignored"]["not_TH"][sample+"_"+name]
rangesList = list(set(rangesList))
		
# Create output ranges file
ranges = {}
missing_branch = False
for branch in rangesList:
	ranges[branch] = [minimum[branch],maximum[branch],length[branch]]

# Saving output JSON files
with open(output_range_file,"w") as outfile:
	json.dump(ranges, outfile, indent = 4)
with open(output_histdict_file,"w") as outfile:
	json.dump(histdict, outfile, indent = 4)
with open(output_playlist_file,"w") as outfile:
	json.dump(playlist_files, outfile, indent = 4)
with open(output_HistComp_folder+"/"+output_HistComp_file,"w") as outfile:
    json.dump(HistComp_config, outfile, indent = 4)
with open(output_summary_file,"w") as outfile:
	json.dump(summary, outfile, indent = 4)

##########

# Removing unique histrograms from generated hist root files
print("")
if dropUniqueHists:
	f = open(output_summary_file,"r")
	hconfig = json.load(f)
	f.close()
	for sample in samples:
		for name in reconames:

			hfilepath = summary["histograms"][sample+"_"+name]
			hfilename = os.path.basename(hfilepath)
			hfile =  TFile.Open(hfilepath,"update")
			print("Opening "+hfilename+" to remove unique histograms")
			keylist = hfile.GetListOfKeys()
			hkeys = {}
			for i in keylist:
				hkeys[i.GetName()]=i.GetCycle()
			for hname in hkeys.keys():
				if hname in histdict["ignored"]["not_shared"][sample+"_"+name]:
					if hkeys[hname] == 1: hfile.Delete(hname+";1")
			hfile.Close()
			
			# For some reason I have to close the file and reopen it to
			# delete the histogram in which cycle = 2
			hfile =  TFile.Open(summary["histograms"][sample+"_"+name],"update")
			keylist = hfile.GetListOfKeys()
			hkeys = {}
			for i in keylist:
				hkeys[i.GetName()]=i.GetCycle()
			for hname in hkeys.keys():
				if hname in histdict["ignored"]["not_shared"][sample+"_"+name]:
					if hkeys[hname] == 2: hfile.Delete(hname+";2")
			hfile.Close()
	print("")

print("Output files:")
print("   "+os.getcwd()+"/"+output_summary_file)
for sample in samples:
	for name in reconames:
		print("   "+os.getcwd()+"/"+summary["histograms"][sample+"_"+name])
if keepcuts:
	for sample in samples:
		for name in reconames:
			print("   "+summary["passed_events"][sample+"_"+name])
print("   "+os.getcwd()+"/"+output_playlist_file)
print("   "+os.getcwd()+"/"+output_range_file)
print("   "+output_HistComp_folder+"/"+output_HistComp_file+"\n")

#energy_from_mc
#energy_from_mc_fraction
#energy_from_mc_fraction_of_highest
#muon_fuzz_energy
#recoName_r_minos_trk_bdL
#recoName_r_minos_trk_end_dcosz
#recoName_r_minos_trk_vtx_dcosz
#recoName_t_minos_trk_numFSMuons
#recoName_t_minos_trk_primFSLeptonPDG




