#include "THistComparator.hh"

#include "TH1.h"
#include "THistComp.hh"

#include <iostream>
using std::cout;
using std::endl;

THistComparator::THistComparator()
: _minProb( 1.0 ), _maxProb( -1 ),
  _minQual( 999e20 ), _maxQual( -999e20 ),
  _minNdof( 99999999 ), _maxNdof( 0 ),
  _testType( "None" ),
  _passed( false ), _prob( 0 ), _quality( 0 ), _ndof( 0 )
{}

THistComparator::THistComparator( Double_t minProb, Double_t maxProb, 
                                  Double_t minQual, Double_t maxQual,
		                  Int_t    minNdof, Int_t    maxNdof,
				  const TString & type )
: _minProb( minProb ), _maxProb( maxProb ),
  _minQual( minQual ), _maxQual( maxQual ),
  _minNdof( minNdof ), _maxNdof( maxNdof ),
  _testType( type ),
  _passed( false ), _prob( 0 ), _quality( 0 ), _ndof( 0 )
{}

THistComp1D * THistComparator::compare( TH1 * h1, TH1 * h2, Result & testStat ) 
{
  if ( h1 == NULL || h2 == NULL )
  { 
    testStat = NOT_TESTED;
    return NULL;
  }
  
  // Check for the same range. No comparison
  // if there is a mis-match
  
  if ( ( h1->GetBinLowEdge(1) != h2->GetBinLowEdge(1) )
       ||
       (h1->GetBinLowEdge(h1->GetNbinsX()+1) != h2->GetBinLowEdge(h2->GetNbinsX()+1)) )
  {
    testStat = ERROR;
    
    printf( "TKsHistComparator:  Hist range mis-match in %s comparison for %s\n",
            testType().Data(), h1->GetName() );
    printf( "    Low x 1 = %f  LowX 2 = %f\n\
    HighX1 = %f  HighX 2 = %f\n\
    Nbin 1 = %i  Nbin 2  = %i\n", h1->GetBinLowEdge(1), h2->GetBinLowEdge(1), 
                                  h1->GetBinLowEdge(h1->GetNbinsX()+1),
                                  h2->GetBinLowEdge(h2->GetNbinsX()+1),
                                  h1->GetNbinsX(), h2->GetNbinsX() );
    return NULL;
  }
  else
  {
    testStat = OK;
  }

  return NULL;
}




TKsHistComparator::TKsHistComparator( Double_t minProb, Double_t maxProb, bool useDist )
:  THistComparator( minProb, maxProb, -9.99E20, 999e20, -1, 99999999,
                    useDist ? "KSdist" : "KSprob" ),
   _useDist(useDist)
{}



THistComp1D * TKsHistComparator::compare( TH1 * h1, TH1 * h2, Result & testStat )
{    
  // Can create comparison object. Then check for 
  // contents in both histograms.
  
  _passed = false;
  _prob   = 0;
  
  THistComparator::compare( h1, h2, testStat );
  if ( testStat != OK )
  {
    return NULL;
  }
  
  THistComp1D * hc = new THistComp1D( h1, h2, 0, 0, 0, false, testType() );
  if ( h1->GetEntries() > 0 && h2->GetEntries() > 0 )
  {
//if ( strcmp( h1->GetName(), "dt1" ) == 0 )
// {
//   h1->Draw();
//   h2->Draw("same");
//   cout << h1->GetName() << " & " << h2->GetName() 
//        << " in TKsHistComparator" << endl;
//   cout << "nbins = " << h1->GetNbinsX() << "  " << h2->GetNbinsX() << endl;
//   cout << "xlow = " << h1->GetBinLowEdge(1) << "  " 
//        << h2->GetBinLowEdge(1) << endl;
//   cout << "xhigh = " << h1->GetBinLowEdge(h1->GetNbinsX()) << "  "
//        << h2->GetBinLowEdge(h2->GetNbinsX()) << endl;
// }

    Double_t prob = h1->KolmogorovTest( h2, _useDist ? "U0M" : "U0" );
    _passed = ( prob >= _minProb && prob <= _maxProb );
    hc->setPassed( _passed );
    hc->setProb( prob );
  }
  else
  {
    testStat = ERROR;
  }  
  return hc;
}



// THistComparator::Result THistComparator::compare( THistComp2D * )
// {}


