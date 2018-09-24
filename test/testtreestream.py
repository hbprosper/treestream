#!/usr/bin/env python
# ----------------------------------------------------------------------------
# File: testtreestream.py
# Created: 06-Jul-2013 Harrison B. Prosper
# Updated: 23-Sep-2018 HBP - use ctypes
# ----------------------------------------------------------------------------
import os, sys
from array import array
from ROOT import *
from treestream import *
from ctypes import c_int, c_double
# ----------------------------------------------------------------------------
def main():
    print "treestream: read/write test"

    oustream = otreestream("test_py.root", "Events", "Test")

    ht      = c_double()
    njet    = c_int()
    jetet   = vector("double")(20)
    astring = string(" "*80)
        
    oustream.add("HT", ht)
    oustream.add("njet", njet)
    oustream.add("jetEt[njet]", jetet)
    oustream.add("astring", astring)
    
    rand    = TRandom3()
    entries = 1400
    step    = 200

    for entry in range(entries):
        
        njet.value = rand.Integer(10)
        jetet.clear()
        ht.value = 0.0
        for i in range(njet.value):
            jetet.push_back(rand.Exp(10))
            ht.value += jetet[i]
        astring.assign("event: %5d njet = %2d" % (entry + 1, njet.value))

        oustream.commit()

        if entry % step == 0:
            print "%5d%5d%10.2f (%s)" % (entry, jetet.size(), ht.value, astring)
        
    oustream.close()

    # ----------------------------------------------------------------------------
    instream = itreestream("test_py.root", "Events")
  
    ENTRIES = instream.entries()
    instream.ls()

    HT      = c_double()
    JETET   = vector("float")(20)
    ASTRING = string(" "*80)

    instream.select("jetEt",   JETET)
    instream.select("astring", ASTRING)
    instream.select("HT",      HT)
    
    for entry in range(ENTRIES):
        instream.read(entry)

        if entry % step == 0:
            print "%5d%5d%10.2f (%s)" % (entry, JETET.size(), HT.value, ASTRING)
        
    instream.close()    
# -------------------------------------------------------------
main()


