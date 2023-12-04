import os, sys
try:
    import ROOT
except:
    sys.exit('** you need to setup ROOT')

try:
    prefix = os.environ['TREESTREAM_PREFIX']
except:
    try:
        prefix = os.environ['CONDA_PREFIX']
    except:
        sys.exit('** neither TREESTREAM_PREFIX nor CONDA_PREFIX defined')

try:
 
   ROOT.gSystem.Load('%s/lib/libtreestream' % prefix)
   from ROOT import itreestream, otreestream, testme
   print("loaded treestream")
except:
   print("** Unable to load treestream")


