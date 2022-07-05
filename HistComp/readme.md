To run the comparitor

make certain you have root set up 



 `export  $TUPLECOMPARISONROOT=where you've cloned TupleComparison`
 
set  
``` 
  $HIST1=<firstfilepath>
  $HIST2=<secondffilepath> 
```  
cd $TUPLECOMPARISONROOT/HistComp

type 

`make` to build the code
  
type
  
  `python runcompareMnv.py $HIST1 $HIST2 output.html`
  
you should get a lot of output and output.html will contain your comparison
  
  
  
