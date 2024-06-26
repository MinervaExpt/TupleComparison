{
  if( gSystem->Getenv("PLOTUTILSROOT") )
  {
    gInterpreter->AddIncludePath( gSystem->ExpandPathName("$PLOTUTILSROOT") );
    gInterpreter->AddIncludePath( gSystem->ExpandPathName("$PLOTUTILSROOT/PlotUtils") );

    string newpath = string(gROOT->GetMacroPath()) + ":" + string(gSystem->ExpandPathName("$PLOTUTILSROOT")) + "/PlotUtils"+":"+ string(gSystem->ExpandPathName("$PLOTUTILSROOT"));

    gROOT->SetMacroPath( newpath.c_str() );
   
    //    gSystem->Load( "libCintex.so" );  // needed to process the dictionaries for the objects
    //Cintex::Enable();
    gSystem->Load( gSystem->ExpandPathName("$PLOTUTILSROOT/libplotutils.so") );
    std::cout << "tried to load libplotutils.so" << endl;
    //gInterpreter->ExecuteMacro("PlotStyle.C");
  }
if( gSystem->Getenv("VALIDATIONTOOLSROOT") )
  {
    gInterpreter->AddIncludePath( gSystem->ExpandPathName("$VALIDATIONTOOLSROOT/HistComp") );
    //    gInterpreter->AddIncludePath( gSystem->ExpandPathName("$PLOTUTILSROOT/PlotUtils") );

    string newpath = string(gROOT->GetMacroPath()) + ":" + string(gSystem->ExpandPathName("$VALIDATIONTOOLSROOT")) + "/HistComp"+":"+ string(gSystem->ExpandPathName("$PLOTUTILSROOT"));

    gROOT->SetMacroPath( newpath.c_str() );
   
    //    gSystem->Load( "libCintex.so" );  // needed to process the dictionaries for the objects
    //Cintex::Enable();
    gSystem->Load( gSystem->ExpandPathName("$VALIDATIONTOOLSROOT/HistComp/libhistcomp.so") );
    std::cout << "tried to load libhistcomp.so" << endl;
    //gInterpreter->ExecuteMacro("PlotStyle.C");
  }  
}

