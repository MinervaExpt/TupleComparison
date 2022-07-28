from ROOT import *
#from MnvConverter import convert
import sys,os,json

f = open(sys.argv[1],'r')
config = json.load(f)
f.close()
summary = json.load(open(config["summary"],'r'))

playlist = summary["playlist"]
reconames = summary["reconames"]
samples = summary["samples"]
histograms = summary["histograms"]

histnames = {}
histpaths = []
for hist in histograms:
	histnames[hist] = os.path.basename(histograms[hist])
	histpaths.append(os.path.dirname(histograms[hist]))
if len(set(histpaths)) == 1:
	histpath = histpaths[0]
else:
	print("\nError: Histograms should all be in the same directory. Exiting comparison.\n")
	sys.exit(1)

summary_HistComp = {
                    "cuts":summary["cuts"],
                    "histogram_path":histpath,
                    "sets":{},
                    "output_htmls":[]
                   }
                    
#####################################################
### Determine which sets of histograms to compare ###
#####################################################
compare_reconames = config["compare_reconames"]
compare_samples = config["compare_samples"]

# Compare every set of histograms to every other set of histograms
if compare_reconames and compare_samples:
	if len(reconames) < 2 or len(samples) < 2:
		print("\nError: You need at least 2 samples and 2 reco names. Exiting comparison.\n")
		sys.exit(1)
	hists = []
	used = []
	for sample in samples:
		for name in reconames:
			hists.append(sample+"_"+name)
	for hist1 in hists:
		used.append(hist1)
		for hist2 in list(set(hists)-set(used)):
			title = playlist+"_"+hist1+"_to_"+hist2
			summary_HistComp["sets"][title] = [histnames[hist1],histnames[hist2]]
# Compare sets with different reco names but from the same sample.
# Will do: Data_CCQENu to Data_MasterAnaDev
# Will NOT do: Data_CCQENu to MC_CCQENu or MC_MasterAnaDev
elif compare_reconames:
	if len(reconames) < 2:
		print("\nError: You need at least 2 reco names (Ex: CCQENu and MasterAnaDev) to compare by reco name. Exiting comparison.\n")
		sys.exit(1)
	used = []
	for name1 in reconames:
		used.append(name1)
		for name2 in list(set(reconames)-set(used)):
			for sample in samples:
				title = playlist+"_"+sample+"_"+name1+"_to_"+name2
				hist1 = histnames[sample+"_"+name1]
				hist2 = histnames[sample+"_"+name2]
				summary_HistComp["sets"][title] = {"hist1":hist1,"hist2":hist2}
# Compare sets from different samples but under the same reco name.
# Will do: Data_CCQENu to MC_CCQENu
# Will NOT do: Data_CCQENu to Data_MasterAnaDev or MC_MasterAnaDev
elif compare_samples:
	if len(samples) < 2:
		print("\nError: You need at least 2 samples (Ex: Data and MC) to compare by sample. Exiting comparison.\n")
		sys.exit(1)
	used = []
	for sample1 in samples:
		used.append(sample1)
		for sample2 in list(set(samples)-set(used)):
			for name in reconames:
				title = playlist+"_"+sample1+"_to_"+sample2+"_"+name
				hist1 = histnames[sample1+"_"+name]
				hist2 = histnames[sample2+"_"+name]
				summary_HistComp["sets"][title] = [hist1,hist2]
else:
	print("\nError: No comparison selections made. Exiting comparison.\n")
	sys.exit(1)

# Create (if necessary) and enter output folder
output_folder = os.path.basename(os.path.dirname(config["summary"]))
if not os.path.isdir(output_folder):
	os.mkdir(output_folder)
os.chdir(output_folder)

for title in summary_HistComp["sets"]:
	summary_HistComp["output_htmls"].append(title+".html")

with open("summary_HistComp.json", "w") as outfile:
	json.dump(summary_HistComp["sets"], outfile, indent = 4)

#path = config["TupleComparisonRoot"]
path = os.getenv("TUPLECOMPARISONROOT")
path_bytes = path.encode('ascii')

print (type(path_bytes),type(path))
if not os.path.exists(path):
  print ("\nError: No validationtoolsroot set. Exiting comparison.\n")
  sys.exit(1)
print("\nLoading some root libraries\n")
gROOT.SetBatch(1)
gInterpreter.AddIncludePath(path)
rootsys = os.getenv("ROOTSYS")
gSystem.Load(rootsys+"/lib/libHist.so");
gSystem.Load(rootsys+"/lib/libRIO.so");
gSystem.Load(rootsys+"/lib/libGui.so");
#newpath = gROOT.GetMacroPath() + ":" + path + "/HistComp"+":"+plotutilsdir;
#print (newpath)
#gROOT.SetMacroPath(newpath)
#print (newpath, type(newpath))
#gROOT.SetMacroPath( newpath)
    
#libpath = os.path.join(path,"HistComp","libhistcomp.so")
#print(libpath)
#gSystem.Load(libpath);
#gROOT.LoadMacro(libpath);
#gROOT.LoadMacro(os.path.join(plotutilsdir,"HistComp","libhistcomp.so"));

######################################################
############### Compare histogram sets ###############
######################################################
for title in summary_HistComp["sets"]:
	thf = TCompareHistFiles()
	thf.enableTest( TCompareHistFiles.KS );
	thf.setScalingType(TCompareHistFiles.EqualArea); # need to make this a variable

	name1 = summary_HistComp["sets"][title]["hist1"]
	name2 = summary_HistComp["sets"][title]["hist2"]
	
	path1 = histpath+"/"+name1
	path2 = histpath+"/"+name2
	
	print ("Comparing "+name1+" to "+name2)
	if not os.path.exists(path1) or not os.path.exists(path2) or os.path.isdir(path1) or os.path.isdir(path2):
		print ("\nError: Can't find one of the input files. Exiting Comparison.\n")
		sys.exit(1)

	thf.getFile1(path1);
	thf.getFile2(path2);

	comp_result = thf.compare();
	outputpage = title+".html"
	print("Saving results to:")
	print("   "+outputpage)
	print("   "+outputpage+".root")
	print("   "+outputpage+"_files/")
	
	thf.writeWebPage(outputpage);
