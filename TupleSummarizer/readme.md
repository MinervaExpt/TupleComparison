#How to run the comparator. 
#set up root.  I use  

source $HOME/conda.sh


go to directory TupleComparison that you downloaded this package into

export $TUPLECOMPARISONROOT=$PWD`

`cd $TUPLECOMPARISONROOT/TupleSummarizer`

`python nu_cuts_v4.py data.txt `

# data.txt is a list of data files

#that will generate an output root file with histograms for each variable in the tuple hist_dat.txt_physical_CCQENu.root and a text file ranges_dat.txt_physical_CCQENu.txt

# physical refers to a set of cuts applied

# CCQENu is the name of the root tree you are actually studying. 

# the ranges file stores the ranges found for the data so that you can then generate a new histogram set with the same ranges.

Next if you want to look at a differnet sample: 

python nu_cuts_v4.py mc.txt ranges_dat.txt_physical_CCQENu.txt

#this analyzes the list of files mc.txt using the ranges you set earlier. 

#this will make a file hist_short.txt_physical_ranges_data_physical_CCQENu_CCQENu.root

# note that the filename now includes the ranges filename so you know what you did.

# now to do the comparison

python $TUPLECOMPARISONROOT/HistComp/runpy3.py hist_data.txt_physical_CCQENu.root hist_short.txt_physical_ranges_data_physical_CCQENu_CCQENu.root diff.html

# diff.html then has all the plots ordered by how bad the comparison is. 



