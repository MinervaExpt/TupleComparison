#include "THistComp.hh"
// #include "TPad.h"
#include "TLatex.h"
#include "TPad.h"
#include "TStyle.h"
#include <iostream>

ClassImp(THistComp)
ClassImp(THistComp1D)

// ClassImp(TGoodHistComp)
// ClassImp(TBadHistComp)

//_____________________________________________________________________________

THistComp::THistComp(Double_t prob, Double_t qual, Int_t ndof, Bool_t passed,
                     const TString & testType )
: fProb( prob ),
  fQual( qual ),
  fNdof( ndof ),
  fPassed( passed ),
  fHistory(), fOrigPath(), fTestType( testType )
{
  gStyle->SetOptStat(0);
}

THistComp::~THistComp() {}


THistComp1D::THistComp1D()
: THistComp( 0, 0, 0, false, "" ), 
  fHist1( NULL ), fHist2( NULL )
{}


THistComp1D::~THistComp1D()
{}


void THistComp1D::DrawRatio()
{
  TH1* hratio=(TH1*)fHist1->Clone("ratio");
  hratio->SetDirectory(0);
  hratio->Divide(fHist2);
  hratio->SetMarkerStyle(1);
  hratio->SetMarkerColor(kBlue);
  hratio->SetLineColor(kBlue);

  // Don't draw errors
  hratio->Draw("hist x");

  hratio->GetYaxis()->SetLabelSize(0.1);
  hratio->GetXaxis()->SetLabelSize(0.1);

  hratio->GetYaxis()->SetNdivisions(505);

  hratio->GetYaxis()->SetRangeUser(0, 2);
}

void THistComp1D::Draw( Option_t * opt )
{
//   if(fHist1->InheritsFrom("TH2")) {
//     printf("Draw for 2D is not implemented\n");
//     return;
//   }
// 
  // std::cout << " start of draw " << std::endl;
  double x;
  //double xmax = 0.;
  double fNorm=-1.0;
  double marker_size = 0.75;
  double scale2=1.0;
  // float scale2 = 1.0;
   double sum1 = fHist1->Integral();
   double sum2 = fHist2->Integral();
 
   if(fNorm<0.0 && sum1>0.0 && sum2>0.0) {   // norm 2 to 1's area
     scale2 = sum1/sum2;
   } 
   else if(fNorm>0.0) {   // norm to a fixed ratio
     scale2 = fNorm;
   }
   double norm2 = fHist2->Integral()*scale2;

  int nx = fHist1->GetNbinsX();
  //  double scale2 = 1;
  double xmin = 1.E90;
  double xmax = -1.E90;
  for (int i=1; i<=nx; i++) {
    x = fHist1->GetBinContent(i);
    
    if (x > xmax) xmax = x;
    if (x < xmin) xmin = x;
    x = fHist2->GetBinContent(i);
    if (x > xmax) xmax = x;
    if (x < xmin) xmin = x;
  }

  fHist1->SetMaximum(xmax*1.1);
  fHist1->SetMinimum(xmin*0.9);
  //std::cout << " start drawing " << std::endl;
  fHist1->SetMarkerSize(marker_size);
  fHist1->SetMarkerStyle(20);
  fHist1->Draw(opt);

  // This should be done already...
  // fHist2->SetNormFactor(norm2);

  //fHist2->SetFillStyle(3013);
  fHist2->SetFillStyle(0);
  //fHist2->SetFillColor(kBlue);    // 41);
  fHist2->SetLineWidth(2);
  fHist2->SetLineColor(kRed);
  fHist2->Draw("hist same");

  fHist1->SetMarkerSize(marker_size);
  fHist1->SetMarkerStyle(20);

  TString optLoc(opt);
  optLoc += ",same";
  fHist1->Draw(optLoc.Data());

  TLatex* tt = new TLatex();
  char tstring[200];
  sprintf(tstring,"PROB=%10.8f",GetProb());
  tt->SetNDC();
  tt->SetText(0.5,0.90,tstring);
  tt->SetTextSize(0.04);
  tt->Draw();
  //printf(" -- opt is %s",optLoc.Data()); 
  gPad->Update();

  printf(" ------------ %s , ks(prob) : %12.5g\n",GetName(),GetProb());
  //  printf(" xmax %f\n",xmax);
  printf(" h1i, h2i = %f  %f\n",fHist1->Integral(), fHist2->Integral());
}

const char* THistComp1D::GetName() const 
{
  static const char* name = "no_name";
  if (fHist1) 
  {
    return fHist1->GetName();
  }
  else 
  {
    return name;
  }
}

