#ifndef TMergeHistFiles_hh
#define TMergeHistFiles_hh

#include "TDirectory.h"
#include "TFile.h"
#include "TObject.h"
#include "TString.h"

#include <string>
#include <vector>

using namespace std;
class TMergeHistFiles : public TObject
{
public:
  TMergeHistFiles( const char * targetFile = "merged.root", 
                   const char * targetDir = "Merge_result" );
  ~TMergeHistFiles();
  
  bool mergeFile( const char * inputFile );
 
  bool writeOutputFile();
 
  // Exclude objects (directories, histograms, etc.) with names 
  // that contain 'excludeString'.
  // An arbitrary number of strings can be added. The substring
  // match must be exact (ie, not a regular expression)
  //
  void addExcludeString( const char * excludeString );
  
  bool copyDir( TDirectory * inDir, TDirectory * outDir );
  bool sumHists( TDirectory * inputDir, TDirectory * mergeDir );
  void printSummary();
  
  TDirectory * resultDirectory() { return _targetDir; }

  void debug( bool on = true ) { _debug = on; }
    
protected:

  TString              _targetDirName;
  TDirectory *         _targetDir;
  TFile *              _targetFile;
  
  Int_t                _nFiles;
  
  Bool_t	       _debug;

  std::vector<std::string> _excludeStrings;

  int                  _nHistCopied;
  int                  _nHistMerged;
  int                  _nDirCopied;
  int                  _nDirMerged;
    
  ClassDef(TMergeHistFiles,1)
};








#endif // TMergeHistFiles_hh
