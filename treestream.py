try:
    import os
    prefix = os.environ['TREESTREAM_PREFIX']
    try:
        import ROOT
        try: 
            ROOT.gSystem.Load('%s/lib/libtreestream' % prefix)
            from ROOT import itreestream, otreestream, testme
            print("loaded treestream")
        except:
            print("** Unable to load treestream")
    except:
        print("** You need to setup ROOT (source thisroot.sh)")
except:
    print("** You need to define TREESTREAM_PREFIX")
    


