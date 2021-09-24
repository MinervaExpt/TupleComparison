from ROOT import *

#from MnvConverter import convert
import sys,os

path = os.getenv("TUPLECOMPARISONROOT")
path_bytes = path.encode('ascii')

print (type(path_bytes),type(path))
if not os.path.exists(path):
  print (" no validationtoolsroot set")
  sys.exit(1)
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
    
libpath = os.path.join(path,"HistComp","libhistcomp.so")
print(libpath)
gSystem.Load(libpath);
#gROOT.LoadMacro(libpath);
#gROOT.LoadMacro(os.path.join(plotutilsdir,"HistComp","libhistcomp.so"));
thf = TCompareHistFiles()
thf.enableTest( TCompareHistFiles.KS );
thf.setScalingType(TCompareHistFiles.EqualArea); # need to make this a variable
name1 = sys.argv[1]
name2 = sys.argv[2]
print (name1)
print (name2)
if not os.path.exists(name1) or not os.path.exists(name2) or os.path.isdir(name1) or os.path.isdir(name2):
  print (" sorry can't find one of the input files")
  sys.exit(1)
newname1 = name1
newname2 = name2  
# need to convert to 1-D hists
#if not "TH" in name1:
#    #name1 = name1.replace(".root","_TH.root")
#    newname1 = (name1)
#else:
#  newname1 = name1
#if not "TH" in name2:
#    #name2 = name2.replace(".root","_TH.root")
#    newname2=convert(name2)
#else:
#    newname2 = name2
print (newname1)
print (newname2)

thf.getFile1(newname1);
thf.getFile2(newname2);

comp_result = thf.compare();
thf.writeWebPage(sys.argv[3]);
