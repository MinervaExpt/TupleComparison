#ifndef THistComp_hh
#define THistComp_hh

#include "TH1.h"
#include "TObject.h"
class THistComp: public TObject 
{
protected:
  Double_t fProb;
  Double_t fQual;
  Int_t    fNdof;
  Bool_t   fPassed;
  
  TString  fHistory;
  TString  fOrigPath;
//  TString  fName;
  TString  fTestType;
  
public:

//   THistComp(Double_t KsProb=0) 
//   : fKsProb( KsProb ),
//     fNorm( 0.0 )
//   {}
  THistComp(Double_t prob, Double_t qual, Int_t ndof, Bool_t passed,
            const TString & testType );

  virtual ~THistComp();
//-----------------------------------------------------------------------------
//  accessors
//-----------------------------------------------------------------------------
  // 0 = no norm, <0=by area, >0 expected hist1 area/hist2 area
  // void SetNorm(Double_t n = 0.0) { fNorm = n; }

  Bool_t     Passed() { return fPassed; }
  Double_t   GetProb() { return fProb; }
  Double_t   GetQuality() { return fQual; }
  Double_t   GetNdof() { return fNdof; }
  const TString & GetTestType() { return fTestType; }
  const TString & GetOrigPath() { return fOrigPath; }
  
  // Double_t   GetProb() { return fKsProb; }
  // Double_t   GetNorm()   { return fNorm; }

  TString& GetHistory() { return fHistory; }

  void setPassed( Bool_t passed ) { fPassed = passed; }
  void setProb( Double_t prob ) { fProb = prob; }
  void setTestType( const TString & tt ) { fTestType = tt; }
  
//  history information
//
  void SetHistory( const TString & hs ) { fHistory = hs; }
  void SetOrigPath( const TString & op ) { fOrigPath = op; }
  
//-----------------------------------------------------------------------------
//  overloaded functions of TObject
//-----------------------------------------------------------------------------
  virtual const char* GetName() const = 0;

  virtual void Browse(TBrowser* b) { Draw("ep"); }

  virtual void Draw(Option_t* Opt="") = 0;  // *MENU*;

  virtual void DrawRatio() = 0;

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
  THistComp1D( TH1 * h1, TH1 * h2, Double_t prob = 0, Double_t qual = 0, 
               Int_t ndof = 0, Bool_t passed = false, 
	       const TString & testType = "" )
  : fHist1( h1 ), fHist2( h2 ),
    THistComp( prob, qual, ndof, passed, testType )
  {}
  virtual ~THistComp1D();
  
  
  TH1*       GetHist1 () { return fHist1;  }
  TH1*       GetHist2 () { return fHist2;  }
  
  virtual void Draw( Option_t* Opt="" );  // *MENU*;
  virtual void DrawRatio();

  virtual void DrawEP() { Draw("ep"); }         // *MENU*;
  
  virtual const char* GetName() const;
 
  void SetHist1( TH1 * h1 ) { fHist1 = h1; }
  void SetHist2( TH1 * h2 ) { fHist2 = h2; } 
  
  ClassDef(THistComp1D,1)
};

// class THistComp2D : public THistComp
// {
// protected:
//   TH2*     fHist1;
//   TH2*     fHist2;
// public:
//   THistComp1D( TH2 * h1, TH2 * h2, Double_t prob, Double_t qual, Int_t ndof,
//                Bool_t passed )
//   : fHist1( h1 ), fHist2( h2 )
//     THistComp( passed, prob, qual, ndof )
//   {}
//   
//   TH2*       GetHist1 () { return fHist1;  }
//   TH2*       GetHist2 () { return fHist2;  }
//   
//   virtual void Draw( Option_t* Opt="" );  // *MENU*;
//   virtual void DrawEP() { Draw("ep"); }         // *MENU*;
//   
//   ClassDef(THistComp2D,1)
// };


#endif



