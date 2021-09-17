/// NOTE NOTE:  need to modify TCompareHistFiles to work off
///             underlying TDirectory*. This would allow operation
///             both from files and memory. The memory case
///             would be useful when merging is involved,
///             so that we don't actually need to write and read
///             any merged files.
///

#include "TMergeHistFiles.hh"

#include "TFolder.h"
#include "TKey.h"
#include "TH1.h"
#include "TROOT.h"

#include <iostream>

// #include "TSystem.h"

using std::cout;
using std::endl;
using std::string;

ClassImp(TMergeHistFiles)

TMergeHistFiles::TMergeHistFiles( const char * targetFile,
                                  const char * targetDir )
:  _nFiles(0),
   _targetFile(0),
   _targetDir(0),
   _targetDirName( targetDir ),
   _nHistCopied(0),
   _nHistMerged(0),
   _nDirCopied(0),
   _nDirMerged(0),
   _debug( false )
{
  _targetFile = new TFile( targetFile, "RECREATE" );
  if ( _targetFile )
  {
    if ( strlen( targetDir ) == 0 )
    {
      _targetDir = _targetFile;
    }
    else
    {
      _targetDir = _targetFile->mkdir( targetDir );
    }
  }
  TH1::AddDirectory( kFALSE );
}


TMergeHistFiles::~TMergeHistFiles()
{}


bool TMergeHistFiles::mergeFile( const char * inputFile )
{
  if ( _targetFile == NULL )
  {
    cout << "TMergeHistFiles::mergeFile Error:  no target file!! Bailing..."
         << endl;
    return false;
  }
  if ( _targetDir == NULL )
  {
    cout << "TMergeHistFiles::mergeFile Error:  no target directory!! "
         << "Bailing..." << endl;
    return false;
  }

  TFile * f = new TFile( inputFile, "READ" );
  if ( f == NULL || !f->IsOpen() )
  { 
    cout << "TMergeHistFiles::mergeFile Error:  Can't open input file \""
         << inputFile << "\"" << endl;
    return false;
  }
  
  if ( _nFiles == 0 )
  {
    ++_nFiles;
    
    // This is the first file. Just copy the contents to
    // the output directory, replicating the directory
    // structure along the way
    
    // _targetDir = new TDirectory( _targetDirName.Data(), "" );
    // gROOT->GetRootFolder()->Add( _targetDir );
    // if ( _debug ) cout << "mergeFile:  creating result dir " 
    //                   << _targetDir->GetName() << endl;
    if ( _debug ) cout << "mergeFile:  copy first file to output file "
                       << _targetFile->GetName() 
		       << " dir " << _targetDir->GetName() << endl;
		       
    copyDir( f, _targetDir );

    if ( _debug )
    {
      cout << "mergeFile:  listing for result dir " << endl;
      _targetDir->ls();
    }
  }
  else
  {
    ++_nFiles;
    if ( _debug ) cout << "mergeFile:  merge histograms from "
                       << "input file " << inputFile << endl
		       << "            "
		       << "into output dir " << _targetDir->GetName() << endl
		       << "            "
		       << "nFiles = " << _nFiles << endl;
   sumHists( f, _targetDir );
  
  }

  f->Close("R");
  delete f;

  return true;
}
  



bool TMergeHistFiles::copyDir( TDirectory * idir, TDirectory * odir )
{
  if ( _debug ) cout << "copyDir:  input dir " << idir->GetName() 
                     << " output dir "
                     << odir->GetName() << endl;
     
  TKey * key;  
  TIter it( idir->GetListOfKeys() );
  while ( (key = dynamic_cast<TKey*>(it.Next())) )
  {
    if ( _debug ) cout << "copyDir:  getting " << key->GetName() << endl;
    TObject * obj = idir->Get( key->GetName() );
    
    // Some objects have bad names that cannot be found using this
    // method, so need to protect against those cases here.
    //
    if ( obj == NULL )
    {
      cout << "copyDir:  input object \"" << key->GetName() 
           << "\" could not be found by key name in " << idir->GetName() 
	   << " . Skipping..." << endl;
      continue;
    }
    
    if ( _debug ) cout << "copyDir:  input obj " << obj->ClassName() 
                       << " named " << obj->GetName() << endl;    
    
    if ( obj->InheritsFrom("TH1") )
    {
       ++_nHistCopied;
       if ( _debug ) cout << "          TH1 sub-class. Clone and add to " 
                          << odir->GetName() << "..." << endl;
			  
       odir->Add( obj->Clone() );
       if ( _debug ) cout << "           ..." << obj->ClassName() 
                          << " cloned and added" << endl;
    }
    else if ( strcmp( obj->ClassName(), "TDirectory" ) == 0 
         ||
         strcmp( obj->ClassName(), "TDirectoryFile" ) == 0 )
    {
      ++_nDirCopied;
      if ( _debug ) cout << "          Directories. Adding new dir to " 
                         << odir->GetName() << endl;
			 
      TDirectory * din = dynamic_cast<TDirectory*>( obj );
      TDirectory * dout = 0;
   
      TObject * o2 = odir->Get( key->GetName() );
      if ( o2 == NULL )
      {
        // Need to create a new directory in the output structure
        //
        // dout = new TDirectory( din->GetName(), "" );
        dout = odir->mkdir( din->GetName() );
      }
      else
      {
        cout << "TMergeHistFiles::copyDir HUGE error. " << endl
	     << "  Found same directory again. "
	     << "This should never happen!!" << endl;
        dout = dynamic_cast<TDirectory*>( o2 );
      }

      if ( _debug ) cout << "          Recursive copyDir call for " 
                         << din->GetName()
                         << " and " << dout->GetName() << endl;
			 
      copyDir( din, dout );
         
      if ( _debug ) cout << "copyDir:  return from recursive call for " 
                         << din->GetName()
                         << " and " << dout->GetName() << endl;
    }
    else // Neither a TH1 nor a directory => forget it
    {
      cout << "copyDir:  ***** Skipping input object class " << obj->ClassName()
           << " named " << obj->GetName() << endl;
    }
  }
  return true;
}

bool TMergeHistFiles::sumHists( TDirectory * din, TDirectory * dsum )
{
  // static ProcInfo_t * info = new ProcInfo_t;
  // gSystem->GetProcInfo( info );
  // cout << "sumHists:  MEMORY usage on entry = " << info->fMemResident << endl;

  if ( _debug )
  {
    cout << "sumHists:  merging directories " << din->GetName() 
         << " and " << dsum->GetName() << endl;
    // cout << "sumHists:  listing for input dir " << din->GetName() << endl;
    // din->ls();
    // cout << "sumHists:  listing for output dir " << dsum->GetName() << endl;
    // dsum->ls();
  }

  TKey * key;
  TIter it( din->GetListOfKeys() );
  while ( (key = dynamic_cast<TKey*>(it.Next())) )
  {
    if ( _debug )
    {
      cout << "sumHists:  searching for key name " << key->GetName() << endl;
    }

    bool skip = false;
    for ( int ii = 0, iiend = _excludeStrings.size() ; ii < iiend ; ++ii )
    {                                                                           
      if ( strstr( key->GetName(), _excludeStrings[ii].c_str() ) )
      {
        if ( _debug )
	{
	  cout << "sumHists:  Name " << key->GetName()
	       << " matches exclude string " << _excludeStrings[ii] 
	       << ". Skipping..." << endl;
	}
        skip = true;
	TObject * oo = din->Get( key->GetName() );
	delete oo;
	break;
      }
    }
    if ( skip ) continue;                                                          
                                            
    TObject * inob  = din->Get(  key->GetName() );
    TObject * outob = dsum->Get( key->GetName() );

    // Some objects have bad names that can't be found using
    // this method, so need to protect against those cases.
    //
    if ( inob == NULL  )
    {
      cout << "sumHist:  input object \"" << key->GetName() 
	   << "\" could not be found by key name in " << din->GetPath()
	   << " . Skipping..." << endl;
      continue;
    }
         
    if ( _debug )
    {
      cout << "           found input class " << inob->ClassName() 
           << " named " << inob->GetName() << endl;
    }
    
    if ( outob )
    {
      if ( _debug )
      {
        cout << "           found output class " << outob->ClassName()
	     << " named " << outob->GetName() << endl;
      }
      
      if ( inob->InheritsFrom("TH1") )
      {
        ++_nHistMerged;
        if ( _debug ) cout << "           "
	                   << "TH1 sub-class, so add input to output...";
     
        TH1 * hin  = static_cast<TH1*>( inob );
        TH1 * hout = dynamic_cast<TH1*>( outob );

	hout->Add( hin, 1 );
        if ( _debug ) cout << "done" << endl;
      }
      else if ( strcmp(inob->ClassName(), "TDirectory") == 0 
                ||
                strcmp( inob->ClassName(), "TDirectoryFile") == 0 )
      {
        ++_nDirMerged;
        if ( _debug )
	{
	  cout << "           "
	       << "Matching directories. Recursive call to sumHists" << endl;
	}

        TDirectory * dinNew  = dynamic_cast<TDirectory*>( inob );
	TDirectory * doutNew = dynamic_cast<TDirectory*>( outob );
	
	sumHists( dinNew, doutNew );

        if ( _debug )
	{
	  cout << "sumHists:  "
	       << "Returned from recursive sumHists call" << endl
	       << "           "
	       << "dirs " << dinNew->GetName() << " and " 
	       << doutNew->GetName() << endl;
	}
      }
      else
      {
	cout << (_debug ? "           " : "sumHists:  ")
	     << "***** Skipping object of " << inob->ClassName()
	     << " named " << inob->GetName() << endl;
      }
    }
    else // no corresponding object in output directory
    {
      if ( _debug )
      {
        cout << "           "
	     << "No matching object in output directory" << endl;
      }
      // If the input object is a new histogram, add it
      // to the output directory. If a new directory,
      // copy it to the output directory. Anything else,
      // forget it.
      //
      if ( inob->InheritsFrom( "TH1" ) )
      {
        ++_nHistCopied;
        if ( _debug )
	{
	  cout << "           "
	       << "TH1 sub-class. Clone and add to output dir "
	       << dsum->GetName() << endl;
        }
        dsum->Add( inob->Clone() );
      }
      else if ( strcmp(inob->ClassName(), "TDirectory") == 0 
                ||
                strcmp(inob->ClassName(), "TDirectoryFile") == 0 )
      {
        ++_nDirCopied;
        if ( _debug )
	{
	  cout << "           "
	       << "New directory. Copy into " << dsum->GetName() << endl;
	}
        // TDirectory * doutNew = new TDirectory( key->GetName(), "" );
	TDirectory * doutNew = dsum->mkdir( inob->GetName() );
        TDirectory * dinFound  = dynamic_cast<TDirectory*>( inob );
  
	copyDir( dinFound, doutNew );
      }
      else
      {
        cout << (_debug ? "           " : "sumHists:  ")
	     << "***** Skipping input object of class " << inob->ClassName()
	     << " named " << inob->GetName() << endl;
       }
        
    
    }
    delete inob;
  }
  return true;
}
      
//       TObject * obj = dsum->CloneObject( o1 );
//       if ( obj ) dsum->Add( obj );
//        
// 	din = static_cast<TDirectory*>( inob );
//         douTDirectory * dout = 0;
//       if ( o2 == NULL )
//       {
//         // Need to create a new directory in the output structure
//         //
//         dout = new TDirectory( key->GetName() );
//         odir->AddDirectory( dout );
//       }
//       else
//       {
//         dout = static_cast<TDirectory*>( o2 );
//       }
// 
//       TObject * obj = dsum->CloneObject( o1 );
//       if ( obj ) dsum->Add( obj );
//    
//    
//     }
//     else
//     {
//       TObject * obj = dsum->CloneObject( o1 );
//       if ( obj ) dsum->Add( obj );
//     }
//  
//  
//  
//   }
//  

bool TMergeHistFiles::writeOutputFile()
{
  _targetFile->Write();
}


void TMergeHistFiles::addExcludeString( const char * excludeString )
{
  _excludeStrings.push_back( excludeString );
  if ( _debug )
  {
    cout << "TMergeHistFiles:  excluding objects with sub-string \""
         << _excludeStrings.back() << endl;
  } 
}


void TMergeHistFiles::printSummary()
{
  cout << "TMergeHistFiles summary:" << endl
       << "  N directories copied = " << _nDirCopied << endl
       << "  N histograms copied  = " << _nHistCopied << endl
       << "  N directories merged = " << _nDirMerged << endl
       << "  N histograms merged  = " << _nHistMerged << endl;
}

