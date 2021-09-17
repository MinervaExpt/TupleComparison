#ifndef THistComp_hh
#define THistComp_hh

#include "TH1.h"

class THistComp: public TObject 
{
protected:
  Double_t fKsProb;
  Double_t fNorm;		// *** is this used anywhere??
  TString  fHistory;
  TString  fOrigPath;
  TString  fName;
public:

  THistComp(Double_t KsProb=0) 
  : fKsProb( KsProb ),
    fNorm( 0.0 )
  {}

  ~THistComp() {}
//-----------------------------------------------------------------------------
//  accessors
//-----------------------------------------------------------------------------
  // 0 = no norm, <0=by area, >0 expected hist1 area/hist2 area
  void SetNorm(Double_t n = 0.0) { fNorm = n; }

  Bool_t     Passed()
  Double_t   GetProb()
  Double_t   GetQuality()
  Double_t   GetNdof()
  const TString & GetTestType()
  const TString & GetOrigPath()
  
  Double_t   GetKsProb() { return fKsProb; }
  Double_t   GetNorm()   { return fNorm; }

  void SetHistory(TString h) { fHistory=h;}
  TString& GetHistory() {return fHistory;}

//  history information
//
  void SetHistory( const TString & hs );
  void SetOrigPath( const TString & op );
  
//-----------------------------------------------------------------------------
//  overloaded functions of TObject
//-----------------------------------------------------------------------------
  virtual const char* GetName() const {
    static const char* name = "no_name";
    if (fHist1) {
      return fHist1->GetName();
    }
    else {
      return name;
    }
  }

  virtual void Browse(TBrowser* b) { Draw("ep"); }

  virtual void Draw(Option_t* Opt="");  // *MENU*;
  virtual void DrawEP() { Draw("ep"); }         // *MENU*;

  ClassDef(THistComp,3)
};


class THistComp1D : public THistComp
{
protected:
  TH1*     fHist1;
  TH1*     fHist2;
public:
  THistComp1D();  // need this to initialize things appropriately
  THistComp1D( TH1 * h1, TH2 * h2, Double_t prob, Double_t qual, Int_t ndof,
               Bool_t passed )
  : fHist1( h1 ), fHist2( h2 ),
    THistComp( passed, prob, qual, ndof )
  {}
  
  TH1*       GetHist1 () { return fHist1;  }
  TH1*       GetHist2 () { return fHist2;  }
  
  virtual void Draw( Option_t* Opt="" );  // *MENU*;
  virtual void DrawEP() { Draw("ep"); }         // *MENU*;
  
  ClassDef(THistComp1D,1)
};

class THistComp2D : public THistComp
{
protected:
  TH2*     fHist1;
  TH2*     fHist2;
public:
  THistComp1D( TH2 * h1, TH2 * h2, Double_t prob, Double_t qual, Int_t ndof,
               Bool_t passed )
  : fHist1( h1 ), fHist2( h2 )
    THistComp( passed, prob, qual, ndof )
  {}
  
  TH2*       GetHist1 () { return fHist1;  }
  TH2*       GetHist2 () { return fHist2;  }
  
  virtual void Draw( Option_t* Opt="" );  // *MENU*;
  virtual void DrawEP() { Draw("ep"); }         // *MENU*;
  
  ClassDef(THistComp2D,1)
};


#endif



