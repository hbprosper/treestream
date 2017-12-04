#!/usr/bin/env python
# ----------------------------------------------------------------------------
# File: testtreestream.py
# Created: 06-July-2013 Harrison B. Prosper
# ----------------------------------------------------------------------------
import os, sys
from array import array
from ROOT import *
# ----------------------------------------------------------------------------
def main():
    print "="*28
    gSystem.Load('$TREESTREAM_PATH/lib/libtreestream')

    out = otreestream("testtreestream.root", "Events", "test treestream")

    # treestream needs objects whose types won't change
    # unexpectedly due to dynamic typing. We get around Python's
    # dynamic typing (for a single variable) by using a single element
    # array. Yes, this is ugly. May fix sometime!

    adouble = array('d'); adouble.append(0)
    along   = array('i'); along.append(0)
    a = vector('double')(500)
    
    out.add("adouble", adouble)
    out.add("along", along)
    out.add('array[along]', a)
    
    random = TRandom3()
    nrows = 1000;
    for row in xrange(nrows):
        adouble[0] = random.Gaus()
        along[0]   = random.Integer(100)
        for ii in xrange(along[0]):
            a[ii] = random.Gaus()
        if row % 100 == 0:
            if along[0] > 0:
                print "%5d %10.3f %10d %10.3f %10.3f" % \
                (row, adouble[0], along[0], a[0], a[along[0]-1])
            else:
                print "%5d %10.3f %10d" % \
                (row, adouble[0], along[0])               
        out.commit()
    out.close()

    print "="*28

    # Now read
    inp = itreestream("testtreestream.root", "")

    adouble = Double()
    along   = Long()
    v       = vector('double')(1000)
    
    inp.select("adouble", adouble)
    inp.select("along", along)
    inp.select("array", v)
    
    for row in xrange(nrows):
        inp.read(row)
        if row % 100 == 0:
            if v.size() > 0:
                print "%5d %10.3f %10d %10.3f %10.3f" % \
                (row, adouble, along, v.front(), v.back())
            else:
                print "%5d %10.3f %10d" % \
                (row, adouble, along)
    inp.close()
# -------------------------------------------------------------
main()


