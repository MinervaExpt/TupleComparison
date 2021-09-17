from ROOT import *
import sys,os
gInterpreter.AddIncludePath( "." )
gSystem.Load("/Applications/root_v6.22.08/lib/libHist.so");
gSystem.Load("/Applications/root_v6.22.08/lib/libRIO.so");
gSystem.Load("/Applications/root_v6.22.08/lib/libGui.so");
newpath = gROOT.GetMacroPath() + ":."# + gSystem.ExpandPathName("$VALIDATIONTOOLSROOT") + "/HistComp"+":"+gSystem.ExpandPat#hName("$PLOTUTILSROOT");
#print newpath, type(newpath)
gROOT.SetMacroPath( newpath)
    
 
gSystem.Load( "./libhistcomp.so" );
gROOT.LoadMacro("/Users/schellma/Dropbox/Tools/ValidationTools/HistComp/libhistcomp.so");
thf = TCompareHistFiles()
thf.enableTest( TCompareHistFiles.KS );
#thf.enableTest( TCompareHistFiles.KSDist);
#thf.setScalingType(TCompareHistFiles.None ); # need to make this a variable
thf.setScalingType(TCompareHistFiles.EqualArea ); # need to make this a variable
name1 = sys.argv[1]
name2 = sys.argv[2]
print name1
print name2
if not os.path.exists(name1) or not os.path.exists(name2) or os.path.isdir(name1) or os.path.isdir(name2):
  print " sorry can't find one of the input files"
  sys.exit(1)
if not "TH" in name1:
    name1 = name1.replace(".root",".root")
if not "TH" in name2:
    name2 = name2.replace(".root",".root")
print name1
print name2

thf.getFile1(name1);
thf.getFile2(name2);

comp_result = thf.compare();
thf.writeWebPage(sys.argv[3]);
