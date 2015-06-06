#!/usr/bin/env python
# ----------------------------------------------------------------------------
# File: testtreestream.py
# Created: 06-July-2013 Harrison B. Prosper
# $Revision:$
# ----------------------------------------------------------------------------
import os, sys
from array import array
from ROOT import *
# ----------------------------------------------------------------------------
def main():
    print "="*28
    gSystem.Load('libtreestream')

    out = otreestream("testtreestream.root", "Events", "test treestream")

    # treestream needs objects whose types won't change
    # unexpectedly due to dynamic typing. We get around Python's
    # dynamic typing (for a single variable) by using a single element
    # array. Yes, this is ugly. May fix sometime!

    adouble = array('d'); adouble.append(0)
    along   = array('i'); along.append(0)

    out.add("adouble", adouble)
    out.add("along", along)

    random = TRandom3()
    nrows = 1000;
    for row in xrange(nrows):
        adouble[0] = random.Gaus()
        along[0]   = random.Integer(100) % 10
        if row % 100 == 0:
            print "%5d %10.3f %10d" % (row, adouble[0], along[0])

        out.commit()
    out.close()

    print "="*28

    # Now read
    inp = itreestream("testtreestream.root", "Events")

    adouble = Double()
    along = Long()
    inp.select("adouble", adouble)
    inp.select("along", along)
    for row in xrange(nrows):
        inp.read(row)
        if row % 100 == 0:
            print "%5d %10.3f %10d" % (row, adouble, along)
    inp.close()
# -------------------------------------------------------------
main()


