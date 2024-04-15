// TCompareHistFiles
// Driver class for histogram comparisons

#ifndef TCompareHistFiles_hh
#define TCompareHistFiles_hh
 
#include "RQ_OBJECT.h"
#include "TFile.h"
#include "TString.h"
#include "TVirtualStreamerInfo.h"
#include "TObject.h"
#include "THistComparator.hh"

#include "TROOT.h"
#include <iostream>
#include <vector>

class TDirectory;
class TFile;
class TH1;
class THistComp;
class THistComparator;
//class TObjArray;


class TCompareHistFiles
{
  RQ_OBJECT("TCompareHistFiles")

public:
  TCompareHistFiles( std::ostream & os=std::cout);
  virtual ~TCompareHistFiles();

  enum TestType
  {
    KS = 1,
    RatioChisq = 2,
    Identical = 0,
    KSDist = 3,
    NTests = 4
  };
  
  enum ScalingType
  {
    None = 0,
    EqualArea = 1,	// scale reference to equal area 
    FixedFactor = 2,	// scale reference by fixed factor
    NScaleTypes = 3
  };
  
  enum SortOption
  {
    NO_SORT          = 0,
    SORT_BY_PROB     = 0X01,
    // SORT_BY_QUAL     = 0X02,
    // SORT_BY_IDENT     = 0X04,
    INCREASING_VALUE = 0X08,
    DECREASING_VALUE = 0X10,
    SORT_ALL         = 0X20,
    SORT_FAILED      = 0X40,
    SORT_PASSED      = 0X80
  };
  
  void getFile1( const char * name ) { _f1 = getFile( name ); }
  void getFile2( const char * name ) { _f2 = getFile( name ); }
  
  void enableTest( TestType t);
  void disableTest( TestType t );
  
  // Note that not all test use all of these
  // quantities to determine pass/fail status
  // 
  void setMinProb( TestType t, Double_t minProb );
  void setMaxProb( TestType t, Double_t maxProb );
  void setMinQuality( TestType t, Double_t minQual );
  void setMaxQuality( TestType t, Double_t maxQual );
  void setMinNdof( TestType t, Int_t minNdof );
  void setMaxNdof( TestType t, Int_t maxNdof );
  
  void setScalingType( ScalingType t ) { _scalingType = t; }
  void setRefScaleFactor( Float_t f )  { _scaleFactor = f; } // only used for FixedFactor
  
  Bool_t compare3();

  Bool_t compareNamed(TString n1, TString n2,
                                         Int_t oDirIndex=0);
  Bool_t compare(TDirectory& d1, TDirectory& d2, Int_t outputDirIndex = 0);

  TFile * getFile( const char* name );
  
  // Output options
  // sortHistComp returns vector of THistComp*'s and 
  // fills the argument vector with approp sorted indices into 
  // that vector
  void setSortTest( TestType so );	// sort on results of this test
  void setSortOption( SortOption so, bool val );
  const std::vector< std::vector<THistComp*> > & allHistComps();
  //
  // Performs the requested sort on the requested parameter,
  // returns a vector of (first) indices into the vector returned
  // by allHistComp()
  void sortHistCompIndices( std::vector<Size_t> & hcIndex );
  
  
  Bool_t writeWebPage( const TString & filename );
  Bool_t saveRootFile( const TString & filename );
   
protected:
  
  std::vector<THistComparator*>  _tests;
  std::vector<TestType>          _testType;
  std::vector<TObjArray*>        _outputDirs;
  std::vector< std::vector<THistComp*> > _histComps;
  
  Bool_t _ksEnabled;
  Bool_t _ratioEnabled;
  Bool_t _identicalEnabled;
  Double_t  _minProb[NTests];
  Double_t  _maxProb[NTests];
  Double_t  _minQual[NTests];
  Double_t  _maxQual[NTests];
  Int_t     _minNdof[NTests];
  Int_t     _maxNdof[NTests];
  
  ScalingType  _scalingType;
  Double_t     _scaleFactor;  // only relevant for FixedFactor scaling
  
  Int_t        _sortTestType;	// use the results of this test to sort
  Int_t        _sortValue;      // the particular variable to sort
  Int_t        _sortDir;
  Int_t        _sortOpt;        // other options, eg, impose pass/fail cuts.
  
  static const TString  _scaleTypeDescr[NScaleTypes];
  
  TFile * _f1;
  TFile * _f2;
  
  std::ostream & _os;
  
  void scaleHist2( TH1 * h1, TH1 * h2 );

  struct ThcList
  {
    THistComp * hc[NTests];
    ThcList()
    {
      for ( int i = 0 ; i < NTests ; ++i )
      { 
        hc[i] = NULL;
      }
    }
    ThcList( const ThcList & cl )
    {
      for ( int i = 0 ; i < NTests ; ++i )
      {
        hc[i] = cl.hc[i];
      }
    }
  };
  ClassDef(TCompareHistFiles,1)
};

#endif // TCompareHistFiles_hh
