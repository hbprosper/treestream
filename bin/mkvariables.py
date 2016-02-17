#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        mkvariables.py
#
#  Description: Scan a simple ntuple and create the file variables.txt that
#               describes its branches and leaves. The file variables.txt has
#               the following fields:
#              
#               type / branch[.leaf] / variable-name / maximum count
#
#               This file can then be used by mkanalyzer.py to create a
#               reasonably comprehensive (first) version of an analyzer.
#
#  Created:     Mon Oct  4, 2010
#  Author:      Harrison B. Prosper
#  Email:       harry@hep.fsu.edu, Harrison.Prosper@cern.ch
#  Fixes:       15-Nov-2010 HBP make sure buffers have a count of at least 1
#               22-Nov-2010 HBP allow multiple trees
#               11-Jan-2011 HBP shorten genparticlehelper variable
#               20-Jul-2011 HBP fix problem with basic type
#               09-Jul-2013 HBP re-order imports to avoid Error message from
#                           root. Also do not convert names to lower case.
#               21-Dec-2014 HBP get rid of xml module
#$Id: mkvariables.py,v 1.19 2013/07/11 01:54:22 prosper Exp $
# ----------------------------------------------------------------------------
import os, sys, re
from string import atof, atoi, replace, lower,\
     upper, joinfields, split, strip, find
from time import sleep, ctime
from ROOT import *
# ----------------------------------------------------------------------------
def usage():
    print '''
mkvariables.py <ntuple-filename> [<tree-name> [<tree-name2...]]
    '''
    sys.exit(0)

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
    from PhysicsTools.TheNtupleMaker.AutoLoader import *
except:
    try:
        gSystem.Load("libtreestream")
    except:
        print "\t** libtreestream not found"
        print '''
    try installing the treestream package:
    
    cd
    mkdir -p external/bin
    mkdir -p external/lib
    mkdir -p external/include
    cd external
    git clone https://github.com/hbprosper/treestream.git

    then
    cd treestream
    make
    make install
    '''        
        sys.exit(0)
# ----------------------------------------------------------------------------
# extract vector type from vector<type>
getvtype = re.compile('(?<=vector[<]).+(?=[>])')
namespace= re.compile('^(edm|reco|pat)')
patname  = re.compile('(?<=pat)[a-z]+[1-9]*')
reconame = re.compile('(?<=reco)[a-z]+[1-9]*')
genname  = re.compile('^(gen[a-z]+|edm[a-z]+)')
countname= re.compile('(?<=^n)(pat|reco)')
# ----------------------------------------------------------------------------
def main():

    # 2nd argument is the TTree name
    if argc > 1:
        # Can have more than one tree
        treename = joinfields(argv[1:], ' ') 
        stream = itreestream(filename, treename)
    else:
        stream = itreestream(filename)
        treename = stream.tree().GetName()

    if not stream.good():
        print "\t** hmmmm...something amiss here!"
        sys.exit(0)
    # list branches and leaves
    stream.ls()

    # write out variables.txt after scanning ntuple listing
    print
    print "==> file: %s" % filename

    tname = split(treename)
    for name in tname:
        print "==> tree: %s" % name
    print "==> output: variables.txt"

    out = open("variables.txt", "w")
    out.write("tree: %s\t%s\n" % (tname[0], ctime()))
    for name in tname[1:]:
        out.write("tree: %s\n" % name)
    out.write("\n")

    # get ntuple listing
    dupname = {} # to keep track of duplicate names

    records = map(split, split(stream.str(),'\n'))
    for x in records:

        # skip junk
        if len(x) == 0: continue
        if x[0] in ["Tree", "Number", ""]: continue

        # Fields:
        # .. branch / type [maximum count [*]]

        # look for variables flagged as leaf counters
        iscounter = x[-1] == "*" # look for a leaf counter
        if iscounter: x = x[:-1] # remove "*" from the end

        if len(x) == 4:
            a, branch, c, btype = x
            maxcount = 1
        elif len(x) == 5:
            a, branch, c, btype, maxcount = x
            maxcount = 1 + 2*atoi(maxcount[1:-1])
        else:
            print "\t**hmmm...not sure what to do with:\n\t%s\n\tchoi!" % x
            sys.exit(0)

        # get branch type in C++ form (not, e.g.,  Double_t)
        btype = replace(lower(btype), "_t", "")
        vtype = getvtype.findall(btype)
        if len(vtype) == 1:
            btype = vtype[0] # vector type
            maxcount = 100   # default maximum count for vectors

## 		# fix a few types
## 		if btype[:-2] in ["32", "64"]:
## 			btype = btype[:-2]
## 		elif btype == "bool":
## 			btype = "int"
## 		elif btype == "uchar":
## 			btype = "int"
## 		elif btype == "uint":
## 			btype = "int"

        # If this is leaf counter, add " *" to end of record
        if iscounter:
            lc = " *"
        else:
            lc = ""

        # make a name for yourself
        # but take care of duplicate names
        t = split(branch, '.')
        bname = t[0]

        if len(t) > 1:
            #t[0] = lower(t[0])			
            a = patname.findall(t[0])
            if len(a) == 0:
                a = reconame.findall(t[0])
                if len(a) == 0:
                    a = genname.findall(t[0])
            if len(a) != 0:
                t[0] = a[0]
        else:
            if len(countname.findall(t[0])) > 0:
                #t[0] = split(lower(countname.sub("", t[0])),'_')[0]
                t[0] = split(countname.sub("", t[0]),'_')[0]
        #t[0] = replace(t[0], 'helper', '')

        # check for duplicate names
        key = t[0]
        if not dupname.has_key(key):
            dupname[key] = [bname, 0]			
        if dupname[key][0] != bname:
            a, n = dupname[key]
            n += 1
            dupname[key] = [bname, n]

        if dupname[key][1] > 0:
            t[0] = "%s%d" % (t[0], dupname[key][1])
        # first strip away namespace
        t[0] = namespace.sub("", t[0])
        name = joinfields(t, '_')
        #print "%s\t%s" % (t[0], bname)

        # write out info for current branch/leaf
        record = "%s/%s/%s/%d %s\n" % (btype, branch, name, maxcount, lc)
        out.write(record)
# ----------------------------------------------------------------------------
main()
