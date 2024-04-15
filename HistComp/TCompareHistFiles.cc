#include "TCompareHistFiles.hh"

#include "THistComp.hh"
#include "THistComparator.hh"

#include "TCanvas.h"
#include "TFile.h"
#include "TFolder.h"
#include "TH1.h"
#include "TKey.h"
#include "TObjArray.h"
#include "TROOT.h"
#include "TSystem.h"

#include <iostream>
#include <map>

using std::cout;
using std::endl;
using std::less;
using std::multimap;
using std::ostream;


const TString 
      TCompareHistFiles::
      _scaleTypeDescr[NScaleTypes] = { "None",
                                       "Equal Area",
			               "Fixed Factor" };
// const TString 
//       TCompareHistFiles::
//       _scaleTypeDescr[TCompareHistFiles::EqualArea]("Equal Area");
// const TString 
//       TCompareHistFiles::
//       _scaleTypeDescr[TCompareHistFiles::FixedFactor]("Fixed Factor");


TCompareHistFiles::TCompareHistFiles(ostream & os)
: _ksEnabled( false ), _ratioEnabled( false ), _identicalEnabled( false ),
  _f1( NULL ), _f2( NULL ),
  _scalingType( None ), _scaleFactor( 1 ), 
  _sortTestType( KS ), _sortValue( SORT_BY_PROB ),
  _sortDir( INCREASING_VALUE ), _sortOpt( SORT_ALL ), _os(std::cout)
  
{
  for ( int i = 0 ; i < NTests ; ++i )
  {
    _minProb[i] = 1;
    _maxProb[i] = 0;
    _minQual[i] =   999E20;
    _maxQual[i] =  -999e20;
    _minNdof[i] = 99999999;
    _maxNdof[i] = 0;
  }  
}


TCompareHistFiles::~TCompareHistFiles()
{}

TFile * TCompareHistFiles::getFile( const char * name )
{
  TFile * file;
  
  file = static_cast<TFile*>( gROOT->GetListOfFiles()->FindObject( name ) );
  if ( file == NULL )
  {
    file = TFile::Open( name );
    if ( !file )
    {
      std::cout << "TCompareHistFiles:  could not open file " << name << endl;
      return NULL;
    }
    else{
      std::cout<<"Found the file "<<name<<std::endl;
    }
  }
  return file;
}
   

void TCompareHistFiles::enableTest( TestType t )
{
  // check that this is not already enabled
  for ( int i = 0; i < _testType.size() ; ++i )
  { 
    if ( _testType[i] == t )
    {
      return;
    }
  }
  _testType.push_back( t );
  
  if ( t == KS || t == KSDist )
  {
    _ksEnabled = true;
    TKsHistComparator * ks = new TKsHistComparator( _minProb[t], _maxProb[t], t==KSDist );
    _tests.push_back ( ks );
    _histComps.push_back( std::vector<THistComp*>() );
  }
  else
  {
    std::cout << "TCompareHistFiles:  Unknown test type " << t << endl;
  }

  return;
}

Bool_t TCompareHistFiles::compare3()
{
  // Prepare output directories for all tests
  //
  for ( int ic = 0, icend = _tests.size() ; ic < icend ; ++ic )
  {
    TDirectory * d = new TDirectory();
    TString name = "Minerva_";
    name.Append( _tests[ic]->testType() );
    name.Append( "_results" );
    d->SetName( name );
cout << "Creating output directory " << name 
     << " for test " << _tests[ic]->testType() << endl;    
    gROOT->GetRootFolder()->Add( d );
    d->Build();
    _outputDirs.push_back( new TObjArray() );
    _outputDirs[ic]->Add( d );
  }

  // Run the comparison
  // (note that the return result is ignored)
  //
  Bool_t comp_result = compare( *_f1, *_f2, 0 );
  
  // Print quick summary for test index 0
  // Base the return result entirely on this test.
  // Return false if any failed.
  //
  int nfail = 0;
  for ( int i = 0, iend = _histComps[0].size() ; i < iend ; ++i )
  {
    //std::cout << _histComps[0].size() << std::endl;
    if ( ! _histComps[0][i]->Passed() ) ++nfail;
  }
  //std::cout << nfail << std::endl;
  std::cout << "Summary of run_comparison test:  " << nfail << " of "
    << _histComps[0].size() << " histograms tested FAILED" << endl;

  return comp_result;
}

Bool_t TCompareHistFiles::compareNamed(TString n1, TString n2,
                                  Int_t oDirIndex){
                                    TDirectory* f1 = TFile::Open(n1.Data(),"READONLY");
                                    TDirectory* f2 = TFile::Open(n2.Data(),"READONLY");

                                 
                                    bool status = compare(*f1, *f2, oDirIndex);
                                    return status;

                                  };

    Bool_t TCompareHistFiles::compare(TDirectory &d1, TDirectory &d2,
                                      Int_t oDirIndex) {
    Bool_t status = true;

    TIter it1(d1.GetListOfKeys());
    TKey *k1;
    TObject *o1, *o2;
    TH1 *h1, *h2;
    THistComp *hc;
    THistComparator::Result result = THistComparator::NOT_TESTED;

    TDirectory *curOutDirs[NTests];
    for (int ic = 0, icend = _tests.size(); ic < icend; ++ic) {
        curOutDirs[ic] =
            static_cast<TDirectory *>(_outputDirs[ic]->operator[](oDirIndex));
    }

    // might want to re-fresh all config settings in case buttons
    // were pushed before objects were defined...?
    // Maybe make sure that does not happen...?
    //
    // cout << "Entering loop over input keys" << endl
    //      << "  Dir1 = " << d1.GetName() << endl
    //      << "  Dir2 = " << d2.GetName() << endl;
    std::cout << "TCompareHistFiles:  scanning directory " << d1.GetName() << endl;

    while ((k1 = static_cast<TKey *>(it1.Next()))) {
        o1 = d1.Get(k1->GetName());
        o2 = d2.Get(k1->GetName());

        // cout<< "Key1 name = " << k1->GetName() << endl;

        if (o2 == NULL) {
            TString type = (o1->InheritsFrom("TH1") &&
                                    !(o1->InheritsFrom("TH2") || o1->InheritsFrom("TH3"))
                                ? "TH1 "
                                : (o1->InheritsFrom("TDirectory")
                                       ? "TDirectory "
                                       : "TObject "));
            std::cout << "TCompareHistFiles: " << o1->ClassName() << " " << o1->GetName()
                << " not found in file 2" << endl;
        } else if (o1->InheritsFrom("TH1") &&
                   !(o1->InheritsFrom("TH2") || o1->InheritsFrom("TH3"))) {
            h1 = static_cast<TH1 *>(o1);
            h2 = static_cast<TH1 *>(o2);

            std::cout << "TCompareHistFiles:      comparing TH1 " << h1->GetName() << endl;

            scaleHist2(h1, h2);

            for (int ic = 0, icend = _tests.size(); ic < icend; ++ic) {
                // cout << "Calling compare for " << _tests[ic]->testType() << endl;
                hc = _tests[ic]->compare(h1, h2, result);
                // cout << "Done in compare" << endl;

                if (result == THistComparator::OK && hc) {
                    // cout << "Comparison OK && THistComp created" << endl
                    //      << "Adding to output dir " << curOutDirs[ic]->GetName() << endl;
                    curOutDirs[ic]->Add(hc);
                    _histComps[ic].push_back(hc);

                    TString path = curOutDirs[ic]->GetPath();
                    path.Remove(path.Index(":"));

                    hc->SetOrigPath(path);
                    hc->SetHistory(TString(" "));
                    // cout << "THistComp comfigured and stored" << endl;

                    // Fail the comparison if the test in the first index
                    // position fails.
                    //
                    if (ic == 0) status &= hc->Passed();
                } else {
                    // cout << "Comparison not OK, or no THistComp created" << endl;
                    THistComp *thc = (hc == NULL ? new THistComp1D() : hc);

                    curOutDirs[ic]->Add(thc);
                    _histComps[ic].push_back(thc);
                }
            }
        } else if ((strcmp(o1->ClassName(), "TDirectory") == 0) ||
                   (strcmp(o1->ClassName(), "TDirectoryFile") == 0)) {
            TDirectory *dd1 = static_cast<TDirectory *>(o1);
            TDirectory *dd2 = static_cast<TDirectory *>(o2);

            std::cout << "TCompareHistFiles:  scanning directory "
                << dd1->GetPath() << endl;

            Int_t newOutputIndex = _outputDirs[0]->GetEntriesFast();

            for (int ic = 0, icend = _tests.size(); ic < icend; ++ic) {
                TDirectory *dnew = new TDirectory();
                dnew->SetName(dd1->GetName());
                dnew->Build();

                // Need to add the directory to it's parent and
                // to the local list of directories
                curOutDirs[ic]->Add(dnew);
                _outputDirs[ic]->AddLast(dnew);
            }
            status &= compare(*dd1, *dd2, newOutputIndex);
            std::cout << "TCompareHistFile:  done with directory "
                << dd1->GetName() << ", continuing with "
                << d1.GetName() << endl;
        } else {
            std::cout << "TCompareHistFiles:  **** skipping obj of class "
                << o1->ClassName() << " with name " << o1->GetName()
                << endl;
        }

    }  // end loop over objects in the input directories

    // cout << "Done with loop over keys" << endl;
    return status;
}

void TCompareHistFiles::setSortOption( SortOption so, bool val )
{
  // Note that we are not enforcing mutual exclusivity.
  // Won't work if that is not imposed by caller.
  //
  // Note:  should simplify all this...
  //
  if ( so & (SORT_BY_PROB) )    // | SORT_BY_QUAL | SORT_BY_IDENT ) )
  {
    _sortValue = so;
  }
  else if ( so & (INCREASING_VALUE | DECREASING_VALUE) )
  {
    _sortDir = so;
  }
  else if ( so & (SORT_ALL | SORT_FAILED | SORT_PASSED | NO_SORT) )
  {
    _sortOpt = so;
  }
}

Bool_t TCompareHistFiles::writeWebPage( const TString & filename  )
{
  // Will write the web page to 'filname', put the plots in
  // the directory 'filename'_files
  //
  // Parse the sorting options to determine which plots to display 
  // and the order they are displayed.
  // 
  // NOTE:  Could move the parsing to the set options method...
  //
  // Will put all tests for a given pair of input plots together.
  //
  typedef multimap<double,ThcList, less<double> > HistCompSet;
    
  HistCompSet sortedComps;

  // Need to get the sorting value (test type + value type)
  
  TString sortDescr;  // NOTE:  fill this eventually
  
  bool sortByProb = (_sortValue == SORT_BY_PROB);
  bool noSort     = (_sortValue == NO_SORT);
  int  testIndx = 0;	// Index into ThcList for test result to be sorted
  bool found = false;
  for ( int i = 0, iend = _tests.size() ; i < iend && !found ; ++i )
  {
    if ( _testType[i] == _sortTestType )
    {  
      testIndx = i;
      found = true;
    }
  }
  if ( !found )
  {
    std::cout << "TCompareHistFiles:  selected sorting test not found! "
        << "Using first found" << endl;
  }
  bool sortAll = (_sortOpt == SORT_ALL);
  bool sortPassed = (_sortOpt == SORT_PASSED);
  bool sortFailed = (_sortOpt == SORT_FAILED);


  std::cout << "Starting results for " << _histComps[0].size() << " hists" << endl;
  // cout << "  Test index = " << testIndx << endl;
  
  for ( int i = 0, iend = _histComps[0].size() ; i < iend ; ++i )
  {
    // Identify the relevant value and check if this one
    // was actually tested
    // 
    // Note:  can get cases where comparison is named but
    // was not actually performed (eg, range mis-match)
    //
// cout << "  Selected test type string = " 
//      << _histComps[testIndx][i]->GetTestType() << endl;
     
    if ( _histComps[testIndx][i]->GetTestType() != "" )
    {
      ThcList ll;
// cout << "    Filling ThcLlist for hist " << i << endl;
      for ( int ic = 0, icend = _tests.size() ; ic < icend ; ++ic )
      {
        ll.hc[ic] = _histComps[ic][i];
      }
// cout << "    Getting sort value" << endl;
      double sortVal = ( sortByProb 
                         ? ll.hc[testIndx]->GetProb() : double( i ) );
// cout << "  Sort value = " << sortVal << endl;
    
      sortedComps.insert( HistCompSet::value_type( sortVal, ll ) );
    }   
  }
// cout << "sortedComps size = " << sortedComps.size() << endl;  
    
  // Now write the web page
  //
  // Get working directory for web page
  //
  TString wdir(filename);
  int nfile = strlen(filename);
  int nbase = strlen(gSystem->BaseName(filename));
  wdir.Remove(nfile-nbase,nbase);

  // Create directory for plots
  //
  TString gifDir( filename );
  gifDir.Append( "_files/" );
  gSystem->mkdir( gifDir, true );

  std::cout << "Writing web page " << filename << endl
      << "Figures written to " << gifDir << endl;
      
// cout << "Filename = " << filename << endl
//      << "Working dir = " << wdir << endl
//      << "gifDir = " << gifDir << endl;
       
  // File for web page
  //

  TString rootFilename(filename);
  rootFilename+=".root";
  TFile outRootFile(rootFilename, "RECREATE");

  FILE * file = fopen( filename, "w" );
  if ( !file )
  {
    std::cout << "TCompareHistFiles:  could not open web page file " 
        << filename << endl;
    return false;
  }
    
  // Start plotting, writing (old school)
  //
  TCanvas * can = new TCanvas();
  const double subPadFrac=0.35;
  const double padHeightRatio=(1-subPadFrac)/subPadFrac;

  const double labelSizeRel=0.06;
  const double yTitleSizeRel=0.07;
  const double xTitleSizeRel=0.1;
  TPad *pad2 = new TPad("pad2", "foo", 0,          0, 1, subPadFrac);
  TPad *pad1 = new TPad("pad1", "foo", 0, subPadFrac, 1,          1);

  // For reasons that are not obvious to me, you have to Draw() the                                                    
  // empty pad in order to be able to do anything useful with it                                                       
  // later. The SetNumber() is so we can get at the pads with TCanvas::cd()                                            
  pad1->SetNumber(1);
  pad2->SetNumber(2);
  pad2->Draw();
  pad1->Draw();
  // SetFillStyle(4000) is a magic code to make the pad transparent,                                                   
  // so we can draw TLatex's without pads covering them                                                                
  can->SetFillStyle(4000);
  pad1->SetFillStyle(4000);
  pad2->SetFillStyle(4000);
  //pad1->SetTopMargin(1.5*pad1->GetTopMargin());                                                                      
  //pad1->SetBottomMargin(0.04);                                                                                       
  pad1->SetBottomMargin(0);
  pad2->SetTopMargin(0);

  pad2->SetBottomMargin(0.35);
  pad2->SetGridy();

  pad1->cd();
  
  // Page header
  //
  fprintf( file, "<html>\n<body>\n" );
  fprintf( file, "Comparison of:<br>\n\t%s<br>\n\tvs.<br>\n\t%s<br>\n", 
           _f1->GetName(), _f2->GetName() );
  if ( noSort )
  {
    fprintf( file, "Unsorted (input order)<br>\n" );
  }
  else if ( sortByProb )
  {
    fprintf( file, "Sorting by KS probability<br>\n" );
    fprintf( file, "Showing all plots<br>\n" );
  }
  
  // Links to plots
  //
  fprintf(file,"<TABLE>\n<TR><TD>Plot</TD><TD>KS Prob</TD></TR>\n");

// int iiicounter=0;
  for ( HistCompSet::iterator ihc = sortedComps.begin(),
        ihcend = sortedComps.end() ; ihc != ihcend ; ++ihc )
  {
// cout << "Creating link to plot " << iiicounter++ << endl;
    THistComp * hc = ihc->second.hc[testIndx];
    TString target( hc->GetOrigPath() );
    target.Append( "_" );
    target.Append( hc->GetName() );
    target.ReplaceAll( " ", "_" );
    target.ReplaceAll( "\t","_" );
    target.ReplaceAll( "\n","_" );
    TString hist( hc->GetOrigPath() );
    hist.Append( "/" );
    hist.Append( hc->GetName() );
    fprintf( file,
             "<TR><TD><a href=\"#%s\">%s</a></TD><TD>%10.8f</TD></TR>\n",
	     target.Data(), hist.Data(), hc->GetProb() );
  }
  fprintf( file, "</TABLE>\n" );
  
  // Now the plots
  //
  for ( HistCompSet::iterator ihc = sortedComps.begin(),
        ihcend = sortedComps.end() ; ihc != ihcend ; ++ihc )
  {
    fprintf( file, "<BR><BR><BR><HR>\n" );
    THistComp * hc = ihc->second.hc[testIndx];
    // 
    // reconstruct target name, write anchor
    //
    TString target( hc->GetOrigPath() );
    target.Append( "_" );
    target.Append( hc->GetName() );
    target.ReplaceAll( " ", "_" );
    target.ReplaceAll( "\t","_" );
    target.ReplaceAll( "\n","_" );
    fprintf( file, "<a name=\"%s\"></a>\n",target.Data());
    
    // The figures. Start with only KStest
    //
    TString gifname = hc->GetName();
    gifname.ReplaceAll(" ","_" );
    gifname.ReplaceAll("\t","_");
    gifname.Append(".gif");
    gifname.Prepend( gifDir );
cout << "    gif file = " << gifname << endl;
    TString label( hc->GetOrigPath() );
    label.Append( "/" );
    label.Append( hc->GetName() );
    fprintf( file, "<H2>%s</H2>\n", label.Data() );
    fprintf( file, "<img src=\"%s\"></img>\n", gifname.Data());

    pad1->cd();
    hc->Draw("e0");
    pad2->cd();
    hc->DrawRatio();

    can->SaveAs( gifname );

    TString canname = hc->GetName();
    canname.ReplaceAll(" ","_" );
    canname.ReplaceAll("\t","_");
    outRootFile.cd();
    can->Write(canname);
  }
  
  fprintf( file, "</body>\n</html>\n" );
  fclose( file );
  can->Close();
  delete can;

  return true;
}

// Protected implementation methods

void TCompareHistFiles::scaleHist2( TH1 * h1, TH1 * h2 )
{
  if ( _scalingType == EqualArea )
  {
    double sum1 = h1->Integral() + h1->GetBinContent(0)
                  + h1->GetBinContent( h1->GetNbinsX() + 1 );
    double sum2 = h2->Integral() + h2->GetBinContent(0)
                  + h2->GetBinContent( h2->GetNbinsX() + 1 );
    if ( sum1 > 0 && sum2 > 0 )
    {
      // NormFactor is the desired normalization of the visible  
      // histogram (ie, excluding under and over-flows). Internally,
      // the bin contents are scaled by NormFactor / Integral. Must
      // therfore multiply the desired scale factor by Integral in order
      // to get the correct NormFactor
      //
      double norm =  sum1 / sum2;
      //h2->SetNormFactor( norm );
      h2->Scale(norm); // HMS need this to make ratio work right.
    }
  }
  else if ( _scalingType == FixedFactor && _scaleFactor != 1.0 )
  {
    h2->SetNormFactor( _scaleFactor * h2->Integral() );
  }
  
  return;
}  



