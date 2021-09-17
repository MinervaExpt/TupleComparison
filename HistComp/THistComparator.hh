// Performs comparison between two histograms.
// Creates appropriate THistComp object, except for 
// any history information
#ifndef THistComparator_hh
#define THistComparator_hh

#include "TString.h"

class TH1;
class TH2;
class THistComp1D;


class THistComparator
{
protected:
  Bool_t   _passed;
  Double_t _prob;
  Double_t _quality;
  Int_t    _ndof;
  TString  _testType;
  
  Double_t _minProb;
  Double_t _maxProb;
  Double_t _minQual;
  Double_t _maxQual;
  Int_t    _minNdof;
  Int_t    _maxNdof;
  
public:

  enum Result
  {
    NOT_TESTED = 0,
    OK = 1,
    ERROR = 999
  };

  THistComparator();
  THistComparator( Double_t minProb, Double_t maxProb, 
                   Double_t minQual, Double_t maxQual,
		   Int_t    minNdof, Int_t    maxNdof,
		   const TString & type );
  virtual ~THistComparator() {}
  
  virtual THistComp1D * compare( TH1 * h1, TH1 * h2, Result & testStat ); 
//  virtual THistComp2D * compare( TH2 * h1, TH2 * h2 );

  Bool_t   passed() { return _passed; }
  Double_t prob()  { return _prob; }
  Double_t quality() { return _quality; }
  Int_t    ndof()   { return _ndof; }
  Bool_t   tested();	// returns 'false' i
  const    TString & testType() { return _testType; }
  
  void setPassed( Bool_t passed )     { _passed = passed; }
  void setProb( Double_t prob )       { _prob = prob; }
  void setQuality( Double_t quality ) { _quality = quality; }
  void setNdof( Int_t ndof )          { _ndof = ndof; }
  
  void setMinProb( Double_t minProb ) { _minProb = minProb; }
  void setMaxProb( Double_t maxProb ) { _maxProb = maxProb; }
  void setMinQual( Double_t minQual ) { _minQual = minQual; }
  void setMaxQual( Double_t maxQual ) { _maxQual = maxQual; }
  void setMinNdof( Int_t minNdof )    { _minNdof = minNdof; }
  void setMaxNdof( Int_t maxNdof )    { _maxNdof = maxNdof; }
  
  ClassDef(THistComparator,1)
};





class TKsHistComparator : public THistComparator
{
public:
  // If useDist, use KS distance instead of KS probability
  TKsHistComparator( Double_t minProb, Double_t maxProb, bool useDist );
  virtual ~TKsHistComparator() {}
  
  virtual THistComp1D * compare( TH1 * h1, TH1 * h2, Result & testStat );
  
protected:
  bool _useDist;
  ClassDef(TKsHistComparator,1)
};


#endif // THistComparator_hh
