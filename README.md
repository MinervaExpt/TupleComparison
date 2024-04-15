# TupleComparison
ROOT TTree comparison utilities from the OSU team.

How to do this. 

git clone this

*To compare histograms*

run setup.sh  it assumes you've set WHEREIPUTMYCODE to directory where you put this code (for example APP)

Then type 

 cmake HistComp
 make
 ln -s libTUPLECOMPARISON.so libTUPLECOMPARISON.dylib

 python runcompare.py <hist1.root> <hist2.root> <output.html>