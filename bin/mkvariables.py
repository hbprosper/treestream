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
#               03-Dec-2017 HBP add name of leaf counter
#               02-Feb-2018 HBP no need to write out leaf counters separately.
#               22-Feb-2018 HBP adapt to improved treestream listing
# ----------------------------------------------------------------------------
import os, sys, re
from string import atof, atoi, replace, lower,\
     upper, joinfields, split, strip, find
from time import sleep, ctime
import ROOT
# ----------------------------------------------------------------------------
def usage():
    sys.exit('''
    Usage:
      mkvariables.py [options] <ntuple-filename> [<tree-name> [<tree-name2...]]

    Options:
      --usetree   Use the treename(s) as struct names
    ''')
# ----------------------------------------------------------------------------
# load treestream module
try:
    from PhysicsTools.TheNtupleMaker.AutoLoader import *
except:
    try:
        print "\tloading treestream\n"
        ROOT.gSystem.Load("$TREESTREAM_PATH/lib/libtreestream")
    except:
        print "\t** libtreestream not found"
        print '''
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
    # get command line arguments
    argv = sys.argv[1:]
    argc = len(argv)
    if argc < 1: usage()

    # check whether to use treename as struct name
    if '--usetree' in argv:
        argv.remove('--usetree')
        usetree = True
        argc   -= 1
    else:
        usetree = False
        
    # get ntuple file name
    filename = argv[0]
    if not os.path.exists(filename):
        sys.exit("\t** file %s not found" % filename)
        
    # 2nd argument is the TTree name
    if argc > 1:
        # Can have more than one tree
        treename = joinfields(argv[1:], ' ')
        print treename
        stream   = ROOT.itreestream(filename, treename)
        if not stream.good():
            sys.exit("\t** hmmmm...something amiss here!")
    
        treenames= stream.treenames();
        tname    = [ x for x in treenames ]
    else:
        stream   = ROOT.itreestream(filename)
        if not stream.good():
            sys.exit("\t** hmmmm...something amiss here!" )
        
        treename = stream.tree().GetName()
        tname    = split(treename)

    # list branches and leaves
    stream.ls()

    # write out variables.txt after scanning ntuple listing
    print
    print "==> file: %s" % filename

    for name in tname:
        print "==> tree: %s" % name
    print "==> output: variables.txt"

    out = open("variables.txt", "w")
    out.write("Tree %s\t%s\n" % (tname[0], ctime()))
    for name in tname[1:]:
        out.write("Tree %s\n" % name)
    out.write("\n")

    # get ntuple listing
    dupname = {} # to keep track of duplicate names

    records = map(split, split(stream.str(),'\n'))
    for x in records:

        # skip junk
        if len(x) == 0: continue
        if x[0] in ["File", "Tree", "Entries", ""]: continue

        # Fields:
        # .. branch / type [maximum count [*]]

        # skip variables flagged as leaf counters
        iscounter = x[-1] == "*" # look for a leaf counter
        if iscounter: continue

        # check if the current branch has a leaf counter
        hascounter = False
        if len(x) == 4:
            a, branch, c, btype = x
            maxcount = 1
        elif len(x) == 5:
            a, branch, c, btype, maxcount = x
            maxcount = atoi(maxcount[1:-1])
        elif len(x) == 7:
            hascounter = True
            a, branch, c, btype, maxcount, d, countername = x
            maxcount = atoi(maxcount[1:-1])
        else:
            sys.exit("\t**hmmm...not sure what to do with:\n\t%s\n\tchoi!" % x)
            
        # get branch type in C++ form (not, e.g.,  Double_t)
        btype = replace(lower(btype), "_t", "")
        vtype = getvtype.findall(btype)
        if len(vtype) == 1:
            btype = vtype[0] # vector type
            maxcount = 100   # default maximum count for vectors

        if hascounter:
            lc = countername
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

        # check whether to include treename in name
        if find(name, '/') > 0:
            t = split(name, '/')
            # this name contains a tree name
            if usetree:
                name = '%s_%s' % (t[0], t[-1])
            else:
                name = t[-1]
        
        # write out info for current branch/leaf
        record = "%s\t%s\t%s %d %s\n" % (btype, branch, name, maxcount, lc)
        out.write(record)
# ----------------------------------------------------------------------------
main()
