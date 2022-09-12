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
# got fed up of writing the same boilerplate code over and over again.
# 
# The package contains two classes itreestream and otreestream that can
# be called from C++ or Python. This example shows how to
# use them.
#
# Created: 23-Sep-2018 Harrison B. Prosper
# Updated: 23-Jun-2019 HBP test recently added features:
#                      1. can read arrays such as v[*][5] into
#                         vector<vector<T> >
#                      2. can read vector<T> (note vector<vector<T> > not
#                         yet working)
#------------------------------------------------------------------------------
import os, sys
import ROOT as rt
from ctypes import c_int, c_double
from treestream import itreestream, otreestream
#------------------------------------------------------------------------------
def write_ntuple(filename="test.root", treename="Events"):
    from time import ctime

    print("\n\t== WRITE ==\n")
    
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
    HT      = c_double()
    njet    = c_int()
    jetet   = rt.vector("float")(20)
    comment = rt.string(80*' ')
    
    # -------------------------------------------------
    # make variables known to output tree "Events" 
    # by creating a branch for each variable
    # -------------------------------------------------
    stream.add("HT", HT)
    stream.add("njet", njet)
    stream.add("jetet", jetet)
    stream.add("comment", comment)
    
    # -------------------------------------------------
    # loop over data to be written out
    # -------------------------------------------------
    rand    = rt.TRandom3()
    entries = 1000
    step    =  200
    
    record = ''
    for entry in range(entries):

        # generate some data
        njet.value = rand.Integer(10)
        jetet.clear()
        HT.value = 0.0 # see ctypes documentation
        for i in range(njet.value):
            jetet.push_back(rand.Exp(10))
            HT.value += jetet[i]
            
        comment.assign("event: %5d njet = %2d" % (entry + 1, njet.value))

        # commit data to root file
        stream.commit()

        if entry % step == 0:
            print("%5d%5d%10.4f (%s) njet = %2d" % \
                  (entry, jetet.size(), HT.value, comment, njet.value))

    #stream.close()
    open('write.log', 'w').write(record)
#------------------------------------------------------------------------------
def read_ntuple(filename="test.root", treename="Events"):

    print("\n\t== READ ==\n")
    stream = itreestream(filename, treename)
    stream.ls()

    # declare variables to receive data
    # note variable length arrays are mapped to STL vectors and
    # note that here the type differs (float) from that stored
    # in the ntuple (double)
    njet    = c_int()
    ht      = c_double()
    et      = rt.vector("float")(20)
    comment = rt.string(80*' ')

    # select which variables (branches) to 
    # read and where to copy their data.
    stream.select("njet",   njet)
    stream.select("jetet",  et)
    stream.select("HT",     ht)
    stream.select("comment", comment)

    step = 200
    entries = stream.entries()
    record = ''
    for entry in range(entries):
        stream.read(entry)

        if entry % step == 0:
            print("%5d%5d%10.4f (%s) njet = %2d" % \
                  (entry, et.size(), ht.value, comment, njet.value))
        
    stream.close()
    open('read.log', 'w').write(record)
#------------------------------------------------------------------------------
def main():
    write_ntuple()
    print('==== Before end ===')
    #read_ntuple()

main()

