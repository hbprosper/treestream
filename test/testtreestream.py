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
#                      1. can read arrays such as v[*][5] into vector<vector<T> >
#                      2. can read vector<T> (note vector<vector<T> > not
#                         yet working)
#------------------------------------------------------------------------------
import os, sys
import ROOT as rt
from ctypes import c_int, c_double
from treestream import itreestream, otreestream
#------------------------------------------------------------------------------
ENTRIES = 10
STEP    = 2
#------------------------------------------------------------------------------
def printit(entry, et, ht, vf, vi, vd, comment):
    s = ''
    s += "%5d\n" % entry
    s += "\tlen(et):       %5d, ht = %8.2f, '%s'\n" % (et.size(), ht.value, comment)
    s += "\tlen(vfloat):   %5d\n" % vf.size()
    if vf.size() > 0:
        s += "\t   vfloat[ 0]: %8.2f\t\t" % vf.front()
        s += "vfloat[-1]: %8.2f\n" % vf.back()

    s += "\tlen(vint):     %5d\n" % vi.size()
    if vi.size() > 0:
        s += "\t   vint[ 0]: %5d\t\t" % vi.front()
        s += "vint[-1]: %5d\n" % vi.back()        

    s += "\tlen(vdouble):  %5d\n" % vd.size()
    if vd.size() > 0:
        s += "\t   vdouble[ 0]: %5d\t\t" % vd.front()
        s += "vdouble[-1]: %5d\n" % vd.back()        
    return s
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
    ht      = c_double()
    njet    = c_int()
    jetet   = rt.vector("double")(20)
    vfloat  = rt.vector("float")(20)
    comment = rt.string(80*' ')
    
    # -------------------------------------------------
    # make variables known to output tree "Events" 
    # by creating a branch for each variable
    # -------------------------------------------------
    # create branch HT of type double
    stream.add("ht", ht)

    # create branches njet of type int and et of type
    # float, which together define a ROOT variable 
    # length array, where njet is the counter variable of
    # the array and et is the variable length structure.
    stream.add("et[njet]", jetet)

    # automatically create the counter variable vfloat_size
    stream.add("vfloat", vfloat)

    # create branch comment of type string
    stream.add("comment", comment)
    
    # add STL vectors explicitly
    vint    = rt.vector("int")()
    vdouble = rt.vector("double")()       
    stream.tree().Branch("vint",    "vector<int>", vint)    
    stream.tree().Branch("vdouble", "vector<double>", vdouble)
    
    # -------------------------------------------------
    # loop over data to be written out
    # -------------------------------------------------
    rand    = rt.TRandom3()
    record = ''
    for entry in range(ENTRIES):
        jetet.clear()
        vfloat.clear()
        vdouble.clear()
        
        # generate some data

        m = rand.Integer(8)
        vfloat.resize(m)
        for i in range(m):
            vfloat[i] = rand.Gaus(100)

        m = rand.Integer(10)
        vint.resize(m)
        for i in range(m):
            vint[i] = rand.Integer(100)

        m = rand.Integer(10)
        vdouble.resize(m)
        for i in range(m):
            vdouble[i] = rand.Gaus(100, 10)                 
            
        njet.value = rand.Integer(10)    
        ht.value = 0.0 # see ctypes documentation
        for i in range(njet.value):
            jetet.push_back(rand.Exp(10))
            ht.value += jetet[i]
            
        comment.assign("event: %5d njet = %2d" % (entry, njet.value))

        # commit data to root file
        stream.commit()

        if entry % STEP != 0: continue
            
        s = printit(entry, jetet, ht, vfloat, vint, vdouble, comment)
        record += s

    stream.close()
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
    ht      = c_double()
    et      = rt.vector("float")(20)
    vfloat  = rt.vector("float")(20)
    comment = rt.string(80*' ')

    # select which variables (branches) to 
    # read and where to copy their data.
    stream.select("et",     et)
    stream.select("ht",     ht)
    stream.select("vfloat", vfloat)
    stream.select("comment",comment)

    # these will be handle directly by ROOT
    vint    = rt.vector("int")()
    stream.select("vint", vint)

    vdouble = rt.vector("double")()
    stream.select("vdouble", vdouble)    
    
    entries = stream.entries()
    record = ''
    for entry in range(entries):
        stream.read(entry)

        if entry % STEP != 0: continue

        s = printit(entry, et, ht, vfloat, vint, vdouble, comment)
        record += s
        print(s)
        
    stream.close()
    open('read.log', 'w').write(record)
#------------------------------------------------------------------------------
def main():
    write_ntuple()
    print
    read_ntuple()

main()

