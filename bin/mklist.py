#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        mklist.py
#  Description: make a list of variables in specified ntuple
#  Created:     02-Jan-2018 Harrison B. Prosper
# ----------------------------------------------------------------------------
import os, sys, re
import ROOT
# ----------------------------------------------------------------------------
def usage():
    sys.exit('''
mklist.py <ntuple-filename> [<tree-name> [<tree-name2...]]
    ''')

# get command line arguments
argv = sys.argv[1:]
argc = len(argv)
if argc < 1: usage()

# get ntuple file name
filename = argv[0]
if not os.path.exists(filename):
    print "\t** file %s not found" % filename
    sys.exit(0)
# ----------------------------------------------------------------------------
# load treestream module
try:
    ROOT.gSystem.Load("$TREESTREAM_PATH/lib/libtreestream")
except:
    print "\t** libtreestream not found"
    sys.exit('''
try installing the treestream package:
    
    cd
    mkdir -p external/bin
    mkdir -p external/lib
    mkdir -p external/include
    cd external
    git clone http://github.com/hbprosper/treestream.git

    then
    cd treestream
    make
    make install
    ''')        

def main():
    # 2nd argument is the TTree name
    if argc > 1:
        # Can have more than one tree
        treename = joinfields(argv[1:], ' ')
        stream   = ROOT.itreestream(filename, treename)     
    else:
        stream   = ROOT.itreestream(filename, "")     
        treename = stream.tree().GetName()
        
    if not stream.good():
        print "\t** hmmmm...something amiss here!"
        sys.exit(0)
    # list branches and leaves
    stream.ls()
# ----------------------------------------------------------------------------
main()
