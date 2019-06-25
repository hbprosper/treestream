#!/usr/bin/env python
#------------------------------------------------------------------------------
# Test reading from Delphes file
# Created: 23-Jun-2019 Harrison B. Prosper
#------------------------------------------------------------------------------
import os, sys
import ROOT as rt
from treestream import itreestream
#------------------------------------------------------------------------------
def main():
    filename = "fatjet.root"
    treename = "Delphes"
    stream = itreestream(filename, treename)

    print("\n\tTest reading of variable length arrays\n")
    
    Tau = rt.vector("vector<float>")(20)
    PT  = rt.vector("float")(20)
    
    stream.select("FatJet.Tau[5]", Tau)
    stream.select("Jet.PT", PT)

    entries = stream.entries()
    print("entries: %d" % entries)

    for entry in range(entries):
        stream.read(entry);
        if Tau.size() < 1: continue
      
        print("\nevent: %d" % entry)
      
        print("  PT.size(): %d" %  PT.size())
        for ii in range(PT.size()):
            print("   %5d\t%10.2f" % (ii, PT[ii]))

        print("\n  Tau.size(): %d" % Tau.size())
        for ii in range(Tau.size()):
            print("   %5d\t%d" % (ii, Tau[ii].size()))
            for jj in range(Tau[ii].size()):
                print("   %5d\t%10.2f" % (jj, Tau[ii][jj]))

    stream.close()    
#------------------------------------------------------------------------------
main()


