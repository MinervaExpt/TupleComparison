# How to run the comparator. 

## Setup  

In terminal setup ROOT using the appropriate setup script. If on your local machine and you use conda, `source $HOME/conda.sh` might be how if not done automatically.

Go to directory `/TupleComparison/`, where this package is cloned to. Enter the following lines:

```
export TUPLECOMPARISONROOT=$PWD
cd $TUPLECOMPARISONROOT/TupleSummarizer
```

## First sample

When in `$TUPLECOMPARISONROOT/TupleSummarizer`, to make histograms for the first sample enter:

```
python nu_cuts_v6.py [JSON config file] dataExample.txt
```
Depending on which version of Python ROOT was built with you may have to replace `python` with `python3`.

**Explanation of  contents**  
`[JSON config file]` contains information on 
* which variables to make histograms of
* the list of cut names to be implemented
* the values to cut on

Under the current default setup in place of `[JSON config file]` use
* for antineutrino runs: `antinu_config.json`.
* for neutrino runs: `nu_config.json`.

`dataExample.txt` is a list of data files. Either edit `dataExample.txt` as necessary to point to the correct files or select an appropriate playlist file to replace it.

**Explanation of output**  
If the code runs succesfully it will generate three output files:
* `cut__dataExample__[config filename]__CCQENu.root`: The combined subset of the events in the data files that passed the implemented cuts.
* `hist__dataExample__[config filename]__CCQENu.root`: A ROOT file with histograms for each variable
* `ranges__dataExample__[config filename]__CCQENu.txt`: A text file containing the ranges found for the data so that you can then generate a new histogram set with the same ranges. This is necessary for later variable-by-variable histogram comparisons between the first and second samples.

The file names begin with the descriptor followed by the `__`-separated expressions described below.
* `dataExample` refers the playlist file `dataExample.txt`, minus the `.txt` extension.
* `[config filename]` refers to the `[JSON config file]`, minus the `.json` extension.
* `CCQENu` is the name of the root tree you are actually studying. 

## Second sample

For the second sample replace the playlist file with the appropriate to the second sample (`mcExample.txt` here) and includes a fourth argument indicating range information for each histogram to be created. Enter:

```
python nu_cuts_v6.py [JSON config file] mcExample.txt ranges__dataExample__[config filename]__physical__CCQENu.txt
```
This example uses the range file from the ouput as described above for the first sample.

The output files will be of the form
* `cut__mcExample__[config filename]___[range filename]___CCQENu.root`
* `hist__mcExample__[config filename]___[range filename]___CCQENu.root`
* `range__mcExample__[config filename]___[range filename]___CCQENu.root`

The fourth expression is isolated with `___`'s instead `__`'s because the range filename is likely to contain `__`'s already. In this example `[range filename]` will be

```
ranges__dataExample__[config filename]__physical__CCQENu
```
The current naming conventions are admittedly messy. They will hopefully be improved.

## The comparison

First, ensure that the code in `$TUPLECOMPARISONROOT/HistComp` is compiled. If it is not, enter this with `cd $TUPLECOMPARISONROOT/HistComp` and type `make` to build it. Then return to `$TUPLECOMPARISONROOT/TupleSummarizer` and run the script in the manner shown below.

`python $TUPLECOMPARISONROOT/HistComp/runcompare.py hist__dataExample__[config filename]__CCQENu.root hist__mcExample__[config filename]___[range filename]___CCQENu.root diff.html
`

You can make this shorter by doing

```
export HIST1=$PWD/hist__dataExample__[config filename]__CCQENu.root
export HIST2=$PWD/hist__mcExample__[config filename]___[range filename]___CCQENu.root
```
Then the command is just

```
python $TUPLECOMPARISONROOT/HistComp/runcompare.py $HIST1 $HIST diff.html
```

The output `diff.html` has all the plots ordered by how bad the comparison is. 



