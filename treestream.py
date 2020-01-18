try:
    import ROOT
    ROOT.gSystem.Load('$TREESTREAM_PATH/lib/libtreestream')
    from ROOT import itreestream, otreestream, testme
    print("loaded treestream")
except:
    print("**fail to load treestream")
    


