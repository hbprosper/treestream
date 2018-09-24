#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: testtreestream.py
# Description:
#  
# Writing code to create and and read flat ROOT ntuples (ones that store the
# standard types, int, long, float, double, string and arrays thereof) is a
# routine task. It is so routine in fact that this chore ought to be done
# for you...by a machine. That is the purpose of the package treestream. It
# handles all the boilerplate ROOT code for creating and reading flat ROOT
# ntuples and does so through a very simple interface. treestream is the
# modern incarnation of a package written in 2001 when the author finally
# got fed up of writing the same boilerplate code to create and read flat
# ntuples.
# 
# The package contains two classes itreestream and otreestream that can
# be called from C++ or Python (via PyROOT). This example shows how to
# use them.
#
# Created: 23-Sep-2018 Harrison B. Prosper
#------------------------------------------------------------------------------
import os, sys
import ROOT as rt
from ctypes import c_int, c_double
from treestream import itreestream, otreestream
#------------------------------------------------------------------------------
def write_ntuple(filename="test.root", treename="Events"):
    from time import ctime
    
    stream = otreestream(filename, treename, ctime())

    # declare variables to be written to ntuple
    # warning:
    # since Python is a dynamically typed language, writing
    # njet = 42
    # will change the type of njet! Instead:
    # 1. use the value attribute of the ctypes to get and 
    #    set their values
    # 2. use the STL vector methods in the usual way
    # 3. use the assign method to assign to the STL string
    ht      = c_double()
    njet    = c_int()
    jetet   = rt.vector("double")(20)
    comment = rt.string(80*' ')
    
    # -------------------------------------------------
    # make variables known to output tree "Events" 
    # by creating a branch for each variable
    # -------------------------------------------------
    # create branch HT of type double
    stream.add("HT", ht)
    
    # create branches njet of type int and jetEt of type
    # double. together these define a ROOT variable 
    # length array, where njet is the counter variable of
    # the array and jetEt is the variable length structure
    # with the data, which treestream assumes is modeled
    # with an STL vector. 
    stream.add("njet", njet)
    stream.add("jetEt[njet]", jetet)
    
    # create branch comment of type string
    stream.add("comment", comment)

    # loop over data to be written out
    rand    = rt.TRandom3()
    entries = 1000
    step    = 200
    for entry in range(entries):

        # generate some data
        njet.value = rand.Integer(10)
        jetet.clear()
        ht.value = 0.0 # see ctypes documentation
        for i in range(njet.value):
            jetet.push_back(rand.Exp(10))
            ht.value += jetet[i]
        comment.assign("event: %5d njet = %2d" % (entry + 1, njet.value))

        # commit data to root file
        stream.commit()

        if entry % step == 0:
            print "%5d%5d%10.2f (%s)" % (entry, 
                                         jetet.size(), 
                                         ht.value, 
                                         comment)
    stream.close()
#------------------------------------------------------------------------------
def read_ntuple(filename="test.root", treename="Events"):

    stream = itreestream(filename, treename)
    stream.ls()

    # declare variables to receive data
    # note variable length arrays are mapped to STL vectors and
    # note that here the type differs (float) from that stored
    # in the ntuple (double)
    HT      = c_double()
    ET      = rt.vector("float")(20)
    comment = rt.string(80*' ')

    # select which variables (branches) to 
    # read and where to copy their data.
    stream.select("jetEt",   ET)
    stream.select("comment", comment)
    stream.select("HT",      HT)
    
    entries = stream.entries()
    step    = 200
    for entry in range(entries):
        # read event into memory
        stream.read(entry)
        if entry % step == 0:
            print "%5d%5d%10.2f (%s)" % (entry, 
                                         ET.size(), 
                                         HT.value, 
                                         comment)       
    stream.close()    
#------------------------------------------------------------------------------
def main():
    write_ntuple()
    print
    read_ntuple()

main()

