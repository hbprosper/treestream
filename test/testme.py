#!/usr/bin/env python
# ----------------------------------------------------------------------------
# File: testme.py
# Created: 23-Sep-2018 Harrison B. Prosper
# ----------------------------------------------------------------------------
from ROOT import *
from treestream import testme
from ctypes import c_int, c_double
# ----------------------------------------------------------------------------
def main():

    t = testme()
    
    HT = c_double()
    njet = c_int()

    t.show("HT", HT)
    t.show("njet", njet)
# -------------------------------------------------------------
main()


