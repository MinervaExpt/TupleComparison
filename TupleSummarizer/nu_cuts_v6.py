
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
config = json.load(f := open(sys.argv[1]))
f.close()

playlist = config["playlist"]
abspath = config["absolutepath"]
recoNames = config["recoNames"]
mcIn = config["mcIn"]
dataIn = config["dataIn"]
cutchoice = config["cutchoice"]

if not abspath:
	for name in recoNames:
		mcIn[name] = os.path.join(os.getcwd(),mcIn[name])
		dataIn[name] = os.path.join(os.getcwd(),dataIn[name])

#inputlist = open(sys.argv[1],'r').readlines()

newfolder = playlist[0]
for name in recoNames:
	newfolder = newfolder+"_"+name
if not os.path.isdir(newfolder):
	os.mkdir(newfolder)
os.chdir(newfolder)

haslim = {}
rangesname="ranges_for_"+playlist[0]
listing = open(rangesname+".txt",'w')
minimum = {}
maximum = {}

count = {}
for name in recoNames: count[name] = {"MC":0,"Data":0}

for name in recoNames:

	print("\nBegin tuple "+name+"\n")

	#thechain = TChain(name)  # root -l file.root ; TBrowser b; # would show you this.
	mcchain = TChain(name)
	datachain = TChain(name)
	
	mclist = open(mcIn[name],'r').readlines()
	datalist = open(dataIn[name],'r').readlines()
	
	#for line in inputlist:
	#  inputfile = line.strip()
	#  thechain.Add(inputfile)

	for line in mclist:
		mcfile = line.strip()
		mcchain.Add(mcfile)
	for line in datalist:
		datafile = line.strip()
		datachain.Add(datafile)

	if (DEBUG):
		mcchain.Print()
		datachain.Print()

	TH = "TH1F"

	# set up cuts from the choice you made above

	recoCuts = cuts
	for c in recoCuts: 
		recoCuts[c] = recoCuts[c].replace("RecoName",name)

	thecut = ""
	tag = ""
	for cut in cutchoice:
		thecut += recoCuts[cut] + " && "
		tag +=cut+"_"
	tag = tag[0:-1]
	thecut = thecut[0:-3]

	print("  The cuts are",tag,":",thecut)
	
	##################
	###### DATA ######
	##################
	
	print("\n  Begin "+name+" Data:")
	
	outnameData = dataIn[name].replace(".txt","")
	outnameData = os.path.basename(outnameData)
	outnameData = outnameData+"_"+tag
	cutoutnameData = "cut_"+outnameData
	
	outfileData = TFile(cutoutnameData+".root",'RECREATE')
	
	datatuplename = datachain.GetName()
	print("    Data tuple name:", datatuplename)
	
	# inntuple = thechain.Get(tuplename)
	in_data_ntuple = datachain
	if "TChain" not in str(type(datachain)):
		print (" no TChain in ",datatuplename)
		sys.exit(1)
	if recoCuts != []:
		print ("    building smaller tuples with cuts",thecut)
		datantuple = in_data_ntuple.CopyTree(thecut)
	else:
		datantuple = thecut
	
	# make the output histogram
	histoutnameData = "hist_"+outnameData
	houtData = ROOT.TFile(histoutnameData+".root","RECREATE")
	ROOT.gROOT.SetBatch(True)  # Supresses the drawing canvas
	print("    Output",name,"Data root file name:", histoutnameData,"\n")
	
	for i in datantuple.GetListOfBranches():
		if DEBUG and count[name]["Data"] > 100:
			break
		count[name]["Data"] = count[name]["Data"] + 1

		# figure out if the branch is a variable or an array of variables
		if DEBUG:
			print ("before try", i.GetName())
		if (count[name]["Data"] > -1):
			len = datantuple.GetLeaf(i.GetName()).GetLen()
			branch = i.GetName()
			b = branch
			if name+"_" in branch:
				branch = branch.replace(name+"_","recoName")
			elif name in branch:
				branch = branch.replace(name,"recoName")
			if DEBUG:
				print (branch)
			htemp = 0
			if data and "truth" in branch:
				continue

	# if it is a variable, just histogram it.  Ditto if it is huge, then just glom em all together as one.

		if len == 1 or len > maxlen:
		    mini = 0.0
		    maxa = 0.0
		    if "sz" in branch:
		    	continue
		    # this is some serious root voodoo - use interactive root itself to make a trial histogram to get the ranges into a temporary histogram
		    if not branch in haslim:
		    	datantuple.Draw(b, b + " != - 9999 && "+b+" != - 999")
		    	htemp = gPad.GetPrimitive("htemp")
		    	if TH not in str(type(htemp)):
		    		continue
		    	
		    	mini = htemp.GetBinLowEdge(1)
		    	maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
		    	htemp.Delete()
		    	
		    	text = "%s %g %g %d\n"%(branch,mini,maxa,len)
		    	listing.write(text)
		    	haslim[branch] = True

	# here if you already had limits set and did not use the root voodoo

		    if branch in haslim and branch in minimum:
		    	mini = minimum[branch]
		    	maxa = maximum[branch]

	# now make a histogram with the right range

		    htemp = TH1F("htemp",branch,40,mini,maxa)
		    htemp.Sumw2()
		    
		    if mini == maxa:
		        continue
		        
		    cut = b + " >= " + str(mini) + " && " + b + " <= " + str(maxa)

	# and fill it

		    datantuple.Draw(b+">>htemp",cut)
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
		    if name+"_" in branch:
		    	branch = branch.replace(name+"_","")
		    elif name in branch:
		    	branch = branch.replace(name,"")
		# here if it is a vector - same as the previous
		
		    for j in range(0,len):
		        nubranch = "%s[%d]"%(branch,j)
		        nub = "%s[%d]"%(b,j)
		        branchname = "%s_%d"%(branch,j)
		        bname = "%s_%d"%(b,j)
		        mini = 0.0
		        maxa = 0.0
		        if not branchname in haslim:
		        	datantuple.Draw(nub, nub + " != -9999 && "+nub+" != - 999")
		        	htemp = gPad.GetPrimitive("htemp")
		        	if TH not in str(type(htemp)):
		        		continue
		        	
		        	mini = htemp.GetBinLowEdge(1)
		        	maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
		        	htemp.Delete()
		        	
		        	text = "%s %g %g %d\n"%(branchname,mini,maxa,len)
		        	listing.write(text)
		        	haslim[branchname] = True
		          
		        if branchname in haslim and branchname in minimum:
		        	#print ("vector", mini,minimum[branchname])
		        	mini = minimum[branchname]
		        	maxa = maximum[branchname]
		          
		        htemp = TH1F("htemp",nubranch,40,mini,maxa)
		        htemp.Sumw2()
		        if DEBUG:
		        	htemp.Print()
		        if mini == maxa:
		            continue
		        cut = nub + " >= " + str(mini) + " && " + nub + " <= " + str(maxa)
		        datantuple.Draw(nub+">>htemp",cut) # loops over all events and histograms them.
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
	outfileData.cd()
	datantuple.Write()
	outfileData.Close()
	
	##################
	####### MC #######
	##################
	
	print("\n  Begin "+name+" MC:")

	outnameMC = mcIn[name].replace(".txt","")
	outnameMC = os.path.basename(outnameMC)
	outnameMC = outnameMC+"_"+tag
	cutoutnameMC = "cut_"+outnameMC
	
	outfileMC = TFile(cutoutnameMC+".root",'RECREATE')

	# Figure out what is in your file

	#for key in thechain.GetListOfKeys():
	#    ntuple = thechain.Get(key.GetName())
	#    print "this file has ",ntuple

	# now loop over all the tuples you want to study

	mctuplename = mcchain.GetName()
	print("    MC tuple name:", mctuplename)
	
	# inntuple = thechain.Get(tuplename)
	in_mc_ntuple = mcchain
	if "TChain" not in str(type(mcchain)):
		print (" no TChain in ",mctuplename)
		sys.exit(1)
	if recoCuts != []:
		print ("    Building smaller tuples with cuts", thecut)
		mcntuple = in_mc_ntuple.CopyTree(thecut)
	else:
		mcntuple = thecut
	
	# make the output histogram
	histoutnameMC = "hist_"+outnameMC
	houtMC = ROOT.TFile(histoutnameMC+".root","RECREATE")
	ROOT.gROOT.SetBatch(True)  # Supresses the drawing canvas
	print("    Output",name,"MC root file name:",histoutnameMC)

	# loop over all the variables in the tuple
	#print (ntuple.GetListOfBranches())

	for i in mcntuple.GetListOfBranches():
		if DEBUG and count[name]["MC"] > 100:
			break
		count[name]["MC"] = count[name]["MC"] + 1

	# figure out if the branch is a variable or an array of variables
		if DEBUG:
			print ("before try", i.GetName())
		if (count[name]["MC"] > -1):
			len = mcntuple.GetLeaf(i.GetName()).GetLen()
			branch = i.GetName()
			b = branch
			if name+"_" in branch:
				branch = branch.replace(name+"_","recoName")
			elif name in branch:
				branch = branch.replace(name,"recoName")
			if DEBUG:
				print (branch)
			htemp = 0
			if data and "truth" in branch:
				continue

	# if it is a variable, just histogram it.  Ditto if it is huge, then just glom em all together as one.

		if len == 1 or len > maxlen:
		    mini = 0.0
		    maxa = 0.0
		    if "sz" in branch:
		    	continue
		    # this is some serious root voodoo - use interactive root itself to make a trial histogram to get the ranges into a temporary histogram
		    if not branch in haslim:
		    	mcntuple.Draw(b, b + " != - 9999 && "+b+" != - 999")
		    	htemp = gPad.GetPrimitive("htemp")
		    	if TH not in str(type(htemp)):
		    		continue
		    	
		    	mini = htemp.GetBinLowEdge(1)
		    	maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
		    	htemp.Delete()
		    	
		    	text = "%s %g %g %d\n"%(branch,mini,maxa,len)
		    	listing.write(text)
		    	haslim[branch] = True

	# here if you already had limits set and did not use the root voodoo

		    if branch in haslim and branch in minimum:
		    	mini = minimum[branch]
		    	maxa = maximum[branch]

	# now make a histogram with the right range

		    htemp = TH1F("htemp",branch,40,mini,maxa)
		    htemp.Sumw2()
		    
		    if mini == maxa:
		        continue
		        
		    cut = b + " >= " + str(mini) + " && " + b + " <= " + str(maxa)

	# and fill it

		    mcntuple.Draw(b+">>htemp",cut)
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
		    if name+"_" in branch:
		    	branch = branch.replace(name+"_","")
		    elif name in branch:
		    	branch = branch.replace(name,"")
		# here if it is a vector - same as the previous
		
		    for j in range(0,len):
		        nubranch = "%s[%d]"%(branch,j)
		        nub = "%s[%d]"%(b,j)
		        branchname = "%s_%d"%(branch,j)
		        bname = "%s_%d"%(b,j)
		        mini = 0.0
		        maxa = 0.0
		        if not branchname in haslim:
		        	mcntuple.Draw(nub, nub + " != -9999 && "+nub+" != - 999")
		        	htemp = gPad.GetPrimitive("htemp")
		        	if TH not in str(type(htemp)):
		        		continue
		        
		        	mini = htemp.GetBinLowEdge(1)
		        	maxa = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)
		        	htemp.Delete()
		        	
		        	text = "%s %g %g %d\n"%(branchname,mini,maxa,len)
		        	listing.write(text)
		        	haslim[branchname] = True
		        	
		        if branchname in haslim and branchname in minimum:
		        	#print ("vector", mini,minimum[branchname])
		        	mini = minimum[branchname]
		        	maxa = maximum[branchname]
		          
		        htemp = TH1F("htemp",nubranch,40,mini,maxa)
		        htemp.Sumw2()
		        if DEBUG:
		        	htemp.Print()
		        if mini == maxa:
		            continue
		        cut = nub + " >= " + str(mini) + " && " + nub + " <= " + str(maxa)
		        mcntuple.Draw(nub+">>htemp",cut) # loops over all events and histograms them.
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
	houtMC.Close()
	outfileMC.cd()
	mcntuple.Write()
	outfileMC.Close()
	
listing.close()

