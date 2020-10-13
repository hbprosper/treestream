#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        mklist.py
#  Description: make a list of variables in specified ntuple
#  Created:     02-Jan-2018 Harrison B. Prosper
# ----------------------------------------------------------------------------
import os, sys, re, ROOT
try:
    from treestream import itreestream
except:
    try:
        import PhysicsTools.TheNtupleMaker.AutoLoader
    except:
        print("\t** unable to import treestream")
        sys.exit('''
Try installing the treestream package:
    
    cd
    mkdir -p external/bin
    mkdir -p external/lib
    mkdir -p external/include
    cd external
    git clone https://github.com/hbprosper/treestream

    then
    cd treestream
    make
    source setup.sh
    ''')
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
    sys.exit("\t** file %s not found" % filename)
# ----------------------------------------------------------------------------
def main():
    # 2nd argument is the TTree name
    if argc > 1:
        # Can have more than one tree
        treename = ' '.join(argv[1:])
        stream   = ROOT.itreestream(filename, treename)     
    else:
        stream   = ROOT.itreestream(filename, "")     
        treename = stream.tree().GetName()
        
    if not stream.good():
        sys.exit("\t** hmmmm...something amiss here!")
    # list branches and leaves
    stream.ls()
# ----------------------------------------------------------------------------
main()
