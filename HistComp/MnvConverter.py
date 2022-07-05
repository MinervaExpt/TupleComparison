# converts 2-D to 1-D projections and renames the file with _TH.root at the end
# HMS 9-21-2020
from ROOT import *
from PlotUtils import MnvH1D, MnvH2D
import sys,os,string



def convert(name):
  if "response" in name:
    print (" this is a response, I can't deal with it")
    return None
  file = TFile.Open(name,"READONLY")
  oname = name.replace(".root","_TH.root")
  ofile = TFile.Open(oname,"RECREATE")
  dir = file.GetListOfKeys()
  #dir.Print()


  for key in dir:
   
    file.cd()
    #print key
    #print (key.GetName())
    mnv = file.Get(key.GetName())
    mnv1type = mnv.InheritsFrom(MnvH1D.Class())
    mnv2type = mnv.InheritsFrom(MnvH2D.Class())
    th1type = mnv.InheritsFrom(TH1.Class())
    th2type = mnv.InheritsFrom(TH2.Class())
    efftype = "efficiency" in mnv.GetName() or "fraction" in mnv.GetName()
    response = "response" in mnv.GetName() or "migration" in mnv.GetName()
    if response:
      print ("I cannot process a response",mnv.GetName())
      continue
      
    if (mnv1type or mnv2type) and not response:
      hist = mnv.GetCVHistoWithError()
    else:
      hist=mnv.Clone()
    ofile.cd()
    
    if th1type and not efftype:
      hist.Scale(1.,"width")
      title = hist.GetTitle()+ "; rate per x axis unit"
      hist.SetTitle(title)
    if th1type and not efftype:
      hist.SetMaximum(1.2)
      hist.SetMinimum(0.0)

    
    hist.Write()

    if th2type:
      #print (" is 2D, make projections")
      if "migration" in hist.GetName():
        continue
      hist.GetZaxis().SetTitle("rate per GeV")
      px = hist.ProjectionX()
      py = hist.ProjectionY()
      if(not efftype):
        titleX = px.GetTitle() + ";"+ px.GetXaxis().GetTitle() + ";  rate per x axis unit"
        titleY = py.GetTitle() + ";"+ py.GetXaxis().GetTitle() +"; rate per x axis unit"
        px.Scale(1,"width")
        py.Scale(1,"width")
        px.SetTitle(titleX)
        py.SetTitle(titleY)
      else:
        px.SetMaximum(1.2)
        py.SetMaximum(1.2)
        px.SetMinimum(0.0)
        py.SetMinimum(0.0)
  #    px.GetXaxis().SetTitleSize(0.1)
  #    px.GetYaxis().SetTitleSize(0.1)
  #    py.GetXaxis().SetTitleSize(0.1)
  #    py.GetYaxis().SetTitleSize(0.1)
      px.SetDirectory(0)
      py.SetDirectory(0)
      px.Write()
      py.Write()
 



  return (oname)
  
convert(sys.argv[1])
