#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Description: Create ntuple analyzer using information supplied in a
#              variables.txt file. (See mkvariables.py).
#
# Created: 06-Mar-2010 Harrison B. Prosper
# Updated: 12-Mar-2010 HBP - fix appending of .root
#          08-Jun-2010 HBP - add creation of selector.h
#          02-Sep-2010 HBP - fix variables.txt record splitting bug
#          01-Oct-2010 HBP - add structs
#          02-Oct-2010 HBP - add cloning
#          10-Jan-2011 HBP - merge histFile and skimFile into outputFile
#          11-Mar-2011 HBP - fix naming bug
#          26-Apr-2011 HBP - alert user only if duplicate name is not a leaf
#                            counter
#          04-Jul-2013 HBP - make a better analyzer work area
#          14-Dec-2014 HBP - encapsulate variables within eventStream class
#          17-Dec-2014 HBP - change to eventBuffer since that is a better
#                            name for this class
#          14-May-2015 HBP - make compatible with latest version of Delphes
#          08-Jun-2015 HBP - fix makefile (define sharedlib)
#          13-Feb-2016 HBP - allow possibility to turn on/off branches
#          03-Dec-2017 HBP - get name of leaf counter from variables.txt
#-----------------------------------------------------------------------------
import os, sys, re, posixpath
from string import atof, atoi, replace, lower,\
     upper, joinfields, split, strip, find
from time import sleep, ctime
from glob import glob
#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
getvno = re.compile(r'[0-9]+$')

def usage():
    print '''
    Usage:
       mkanalyzer.py <analyzer-name> [variables.txt]
    '''
    sys.exit(0)

def nameonly(s):
    return posixpath.splitext(posixpath.split(s)[1])[0]

def join(left, a, right):
    s = ""
    for x in a:
        s = s + "%s%s%s" % (left, x, right)
    return s

def getauthor():
    regex  = re.compile(r'(?<=[0-9]:)[A-Z]+[a-zA-Z. ]+')
    record = strip(os.popen("which getent").read())
    if record != "":
        record = strip(os.popen("getent passwd $USER").read())
    author = "Shakespeare's ghost"
    if record != "":
        t = regex.findall(record)
        if len(t) > 0: author = t[0]
    return author
#-----------------------------------------------------------------------------
AUTHOR = getauthor()

if os.environ.has_key("CMSSW_BASE"):
    CMSSW_BASE = os.environ["CMSSW_BASE"]
    PACKAGE = "%s/src/PhysicsTools/TheNtupleMaker" % CMSSW_BASE
    TREESTREAM_HPP = "%s/interface/treestream.h" % PACKAGE
    TREESTREAM_CPP = "%s/src/treestream.cc" % PACKAGE
    TNM_HPP = "%s/interface/tnm.h" % PACKAGE
    TNM_CPP = "%s/src/tnm.cc" % PACKAGE
    TNM_PY  = "%s/python/tnm.py" % PACKAGE
else:
    if os.environ.has_key('TREESTREAM_PATH'):
        area  = {'local': '%s' % os.environ['TREESTREAM_PATH']}
        TREESTREAM_HPP = "%(local)s/include/treestream.h" % area
        TREESTREAM_CPP = "%(local)s/src/treestream.cc" % area
        TNM_HPP = "%(local)s/tnm/tnm.h"  % area
        TNM_CPP = "%(local)s/tnm/tnm.cc" % area
        TNM_PY  = "%(local)s/tnm/tnm.py" % area
    else:
        TREESTREAM_HPP = "treestream.h"
        TREESTREAM_CPP = "treestream.cc"
        TNM_HPP = "tnm.h"
        TNM_CPP = "tnm.cc"
        TNM_PY  = "tnm.py"
    
# Make sure that we can find treestream etc.

if not os.path.exists(TREESTREAM_HPP):
    print "\n** error ** - required file:\n\t%s\n\t\tNOT found!" % \
          TREESTREAM_HPP
    print '''
    try installing treestream package:
    
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

if not os.path.exists(TREESTREAM_CPP):
    print "\n** error ** - required file:\n\t%s\n\t\tNOT found!" % \
          TREESTREAM_CPP
    sys.exit(0)
#-----------------------------------------------------------------------------
LINKDEF = \
  '''
#include <map>
#include <string>
#include <vector>

#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

#pragma link C++ function error;
#pragma link C++ function strip;
#pragma link C++ function split;
#pragma link C++ function change;
#pragma link C++ function nameonly;
#pragma link C++ function shell;
#pragma link C++ function deltaPhi;
#pragma link C++ function deltaR;
#pragma link C++ function fileNames;
#pragma link C++ function setStyle;
#pragma link C++ function particleName;

#pragma link C++ class outputFile;
#pragma link C++ class commandLine;
#pragma link C++ class matchedPair;
#pragma link C++ class ptThing;

#pragma link C++ class itreestream;
#pragma link C++ class otreestream;
#pragma link C++ class eventBuffer;

%(pragma)s
#endif
'''

MACRO_DECL_H =\
'''
//----------------------------------------------------------------------------
// -- Declare variables
//----------------------------------------------------------------------------
struct %(Name)sEvent {
%(vardecl)s
//----------------------------------------------------------------------------
// --- Structs can be filled by calling fillObjects()
//----------------------------------------------------------------------------
%(structdecl)s
%(structimpl)s
%(structimplall)s
}; 
'''

MACRO_IMPL_H =\
'''
%(impl)s
'''

TEMPLATE_H =\
'''#ifndef EVENTBUFFER_H
#define EVENTBUFFER_H
//----------------------------------------------------------------------------
// File:        eventBuffer.h
// Description: Analyzer header for ntuples created by TheNtupleMaker
// Created:     %(time)s by mkanalyzer.py
// Author:      %(author)s
//----------------------------------------------------------------------------
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <map>
#include <cassert>
#include "treestream.h"

struct eventBuffer
{
  //--------------------------------------------------------------------------
  // --- Declare variables
  //--------------------------------------------------------------------------
%(vardecl)s
  //--------------------------------------------------------------------------
  // --- Structs can be filled by calling fill(), or individual fill
  // --- methods, e.g., fillElectrons()
  // --- after the call to read(...)
  //----------- --------------------------------------------------------------
%(structdecl)s
%(structimpl)s
%(structvec)s
%(structimplall)s
   //--------------------------------------------------------------------------
%(selectimpl)s
  //--------------------------------------------------------------------------
  // A read-only buffer 
  eventBuffer() : input(0), output(0), choose(std::map<std::string, bool>()) {}
  eventBuffer(itreestream& stream, std::string varlist="")
  : input(&stream),
    output(0),
    choose(std::map<std::string, bool>())
  {
    if ( !input->good() ) 
      {
        std::cout << "eventBuffer - please check stream!" 
                  << std::endl;
	    exit(0);
      }

    initBuffers();
    
    // default is to select all branches      
    bool DEFAULT = varlist == "";
%(choose)s
    if ( DEFAULT )
      {
        std::cout << std::endl
                  << "eventBuffer - All branches selected"
                  << std::endl;
      }
    else
      {
        std::cout << "eventBuffer - branches selected:"
                  << std::endl;      
        std::istringstream sin(varlist);
        while ( sin )
          {
            std::string key;
            sin >> key;
            if ( sin )
              {
                if ( choose.find(key) != choose.end() )
                  {
                    choose[key] = true;
                    std::cout << "\t" << key << std::endl;
                  }
                else
                  {
                    std::cout << "\t** error ** unknown branch: "
                              << key
                              << std::endl
                              << "Please fix and try again. Bye!"
                              << std::endl;
                    exit(0);
                  }
              }
          }
      }
%(setb)s
  }

  // A write-only buffer
  eventBuffer(otreestream& stream)
  : input(0),
    output(&stream)
  {
    initBuffers();

%(addb)s
  }

  void initBuffers()
  {
%(init)s
  }
      
  void read(int entry)
  {
    if ( !input ) 
      { 
        std::cout << "** eventBuffer::read - first  call read-only constructor!"
                  << std::endl;
        assert(0);
      }
    input->read(entry);

    // clear indexmap
    for(std::map<std::string, std::vector<int> >::iterator
    item=indexmap.begin(); 
    item != indexmap.end();
    ++item)
    item->second.clear();
  }

  void select(std::string objname)
  {
    indexmap[objname] = std::vector<int>();
  }

  void select(std::string objname, int index)
  {
    try
     {
       indexmap[objname].push_back(index);
     }
    catch (...)
     {
       std::cout << "** eventBuffer::select - first call select(""" 
                 << objname << """)" 
                 << std::endl;
       assert(0);
    }
  }

 void ls()
 {
   if( input ) input->ls();
 }

 int size()
 {
   if( input ) 
     return input->size();
   else
     return 0;
 }

 void close()
 {
   if( input )   input->close();
   if( output ) output->close();
 }

 // --- indexmap keeps track of which objects have been flagged for selection
 std::map<std::string, std::vector<int> > indexmap;

 // to read events
 itreestream* input;

 // to write events
 otreestream* output;

 // switches for choosing branches
 std::map<std::string, bool> choose;

}; 
#endif
'''


TEMPLATE_CC =\
'''//---------------------------------------------------------------------------
// File:        %(name)s.cc
// Description: Analyzer for simple ntuples, such as those created by
//              TheNtupleMaker
// Created:     %(time)s by mkanalyzer.py
// Author:      %(author)s
//----------------------------------------------------------------------------
#include "tnm.h"
using namespace std;
//----------------------------------------------------------------------------
int main(int argc, char** argv)
{
  // If you want canvases to be visible during program execution, just
  // uncomment the line below
  //TApplication app("%(name)s", &argc, argv);

  // Get command line arguments
  commandLine cl(argc, argv);
    
  // Get names of ntuple files to be processed
  vector<string> filenames = fileNames(cl.filelist);

  // Create tree reader
  itreestream stream(filenames, "%(treename)s");
  if ( !stream.good() ) error("can't read root input files");

  // Create a buffer to receive events from the stream
  // The default is to select all branches
  // Use second argument to select specific branches
  // Example:
  //   varlist = 'Jet_PT Jet_Eta Jet_Phi'
  //   ev = eventBuffer(stream, varlist)

  eventBuffer ev(stream);
  
  int nevents = ev.size();
  cout << "number of events: " << nevents << endl;

  // Create output file for histograms; see notes in header 
  outputFile of(cl.outputfilename);

  // -------------------------------------------------------------------------
  // Define histograms
  // -------------------------------------------------------------------------
  //setStyle();

  // -------------------------------------------------------------------------
  // Loop over events
  // -------------------------------------------------------------------------
  
  for(int entry=0; entry < nevents; entry++)
    {
      // read an event into event buffer
      ev.read(entry);

      // Uncomment the following line if you wish to copy variables into
      // structs. See the file eventBuffer.h to find out what structs
      // are available. Alternatively, you can call individual fill functions,
      // such as, ev.fillElectrons().
      //ev.fillObjects();

      // analysis
    }
    
  ev.close();
  of.close();
  return 0;
}
'''


PYTEMPLATE =\
'''#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        %(name)s.py
#  Description: Analyzer for simple ntuples, such as those created by
#               TheNtupleMaker
#  Created:     %(time)s by mkanalyzer.py
#  Author:      %(author)s
# ----------------------------------------------------------------------------
import os, sys, re
from tnm import *
from ROOT import *
# ----------------------------------------------------------------------------
# -- Constants, procedures and functions
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
def main():

    cl = commandLine()
    
    # Get names of ntuple files to be processed
    filenames = fileNames(cl.filelist)

    # Create tree reader
    stream = itreestream(filenames, "%(treename)s")
    if not stream.good():
        error("can't read input files")

    # Create a buffer to receive events from the stream
    # The default is to select all branches.
    # Use second argument to select specific branches
    # Example:
    #   varlist = 'Jet_PT Jet_Eta Jet_Phi'
    #   ev = eventBuffer(stream, varlist)
    #
    ev = eventBuffer(stream)

    nevents = ev.size()
    print "number of events:", nevents

    # Create file to store histograms
    of = outputFile(cl.outputfilename)

    # ------------------------------------------------------------------------
    # Define histograms
    # ------------------------------------------------------------------------
    setStyle()

    # ------------------------------------------------------------------------
    # Loop over events
    # ------------------------------------------------------------------------
    
    for entry in xrange(nevents):
        ev.read(entry)

        # Uncomment the following line if you wish to copy variables into
        # structs. See the header eventBuffer.h to find out what structs
        # are available. Alternatively, you can call individual fill
        # functions, such as ev.fillJets().
        #ev.fillObjects();

        # analysis
        
    ev.close()
    of.close()
# ----------------------------------------------------------------------------
try:
   main()
except KeyboardInterrupt:
   print "bye!"
'''

MAKEFILE = '''#----------------------------------------------------------------------------
# Description: Makefile to build analyzers
# Created:     %(time)s by mkanalyzer.py
# Author:      %(author)s
#----------------------------------------------------------------------------
ifndef ROOTSYS
$(error *** Please set up Root)
endif

name    := %(name)s

# Sub-directories
srcdir	:= src
tmpdir	:= tmp
libdir	:= lib
incdir	:= include

$(shell mkdir -p tmp)
$(shell mkdir -p lib)

# Set this equal to the @ symbol to suppress display of instructions
# while make executes
ifdef verbose
AT 	:=
else
AT	:= @
endif
#-----------------------------------------------------------------------
# sources and objects
#-----------------------------------------------------------------------
header  := $(incdir)/tnm.h
linkdef := $(incdir)/linkdef.h
cinthdr := $(srcdir)/dictionary.h
cintsrc := $(srcdir)/dictionary.cc

# Construct list of sources to be compiled into applications
appsrcs	:= $(wildcard *.cc)
appobjects	:= $(addprefix $(tmpdir)/,$(appsrcs:.cc=.o))

# Construct list of applications
applications := $(appsrcs:.cc=)

# Construct list of sources to be compiled into shared library
ccsrcs	:= $(filter-out $(cintsrc),$(wildcard $(srcdir)/*.cc))
sources	:= $(ccsrcs) $(cintsrc)
objects	:= $(subst $(srcdir)/,$(tmpdir)/,$(sources:.cc=.o))

# Display list of applications to be built
#say	:= $(shell echo "appsrcs:     $(appsrcs)" >& 2)
#say	:= $(shell echo "appobjects:  $(appobjects)" >& 2)
#say	:= $(shell echo "objects:     $(objects)" >& 2)
#$(error bye!) 

#-----------------------------------------------------------------------
# 	Define which compilers and linkers to use
#-----------------------------------------------------------------------
# If clang++ exists use it, otherwise use g++
COMPILER:= $(shell which clang++)
ifneq ($(COMPILER),)
CXX     := clang++
LINK	:= clang++
else
CXX     := g++
LINK	:= g++
endif 
CINT	:= rootcint

#-----------------------------------------------------------------------
# 	Define paths to be searched for C++ header files (#include ....)
#-----------------------------------------------------------------------
CPPFLAGS:= -I. -I$(incdir) -I$(srcdir) $(shell root-config --cflags) 

# 	Define compiler flags to be used
#	-c		perform compilation step only 
#	-g		include debug information in the executable file
#	-O2		optimize
#	-ansi	require strict adherance to C++ standard
#	-Wall	warn if source uses any non-standard C++
#	-pipe	communicate via different stages of compilation
#			using pipes rather than temporary files

CXXFLAGS:= -c -g -O2 -ansi -Wall -pipe -fPIC

#	C++ Linker
#   set default path to shared library
LD	:= $(LINK) -Wl,-rpath,$(PWD)/$(libdir)

OS	:= $(shell uname -s)
ifeq ($(OS),Darwin)
    LDSHARED	:= $(LD) -dynamiclib
    LDEXT       := .dylib
else
    LDSHARED	:= $(LD) -shared
    LDEXT       := .so
endif

#	Linker flags

LDFLAGS := -g

# 	Libraries

LIBS	:=  \
$(shell root-config --libs) -L$(libdir) -lMinuit -lMathCore

sharedlib := $(libdir)/libtnm$(LDEXT)

#-----------------------------------------------------------------------
#	Rules
#	The structure of a rule is
#	target : source
#		command
#	The command makes a target from the source. 
#	$@ refers to the target
#	$< refers to the source
#-----------------------------------------------------------------------
all:	$(sharedlib) $(applications) 

bin:	$(applications)

lib:	$(sharedlib)

# Syntax:
# list of targets : target pattern : source pattern

# Make applications depend on shared libraries to force the latter
# to be built first

$(applications)\t: %(percent)s\t: $(tmpdir)/%(percent)s.o  $(sharedlib)
\t@echo "---> Linking $@"
\t$(AT)$(LD) $(LDFLAGS) $< $(LIBS) -ltnm -o $@

$(appobjects)\t: $(tmpdir)/%(percent)s.o\t: %(percent)s.cc
\t@echo "---> Compiling application `basename $<`" 
\t$(AT)$(CXX) $(CXXFLAGS) $(CPPFLAGS)  $< -o $@ # >& $*.FAILED
\t@rm -rf $*.FAILED

$(sharedlib)\t: $(objects)
\t@echo "---> Linking `basename $@`"
\t$(AT)$(LDSHARED) $(LDFLAGS) -fPIC $(objects) $(LIBS) -o $@

$(objects)	: $(tmpdir)/%(percent)s.o	: $(srcdir)/%(percent)s.cc
\t@echo "---> Compiling `basename $<`" 
\t$(AT)$(CXX) $(CXXFLAGS) $(CPPFLAGS)  $< -o $@ # >& $*.FAILED
\t$(AT)rm -rf $*.FAILED

$(cintsrc)  : $(header) $(linkdef)
\t@echo "---> Generating dictionary `basename $@`"
\t$(AT)$(CINT) -f $@ -c -I. -Iinclude -I$(ROOTSYS)/include $+
\t$(AT)mv $(srcdir)/*.pcm $(libdir)

# 	Define clean up rules
clean   :
\trm -rf $(tmpdir)/* $(libdir)/* $(srcdir)/dictionary* $(applications)
'''

README = '''Created: %(time)s

    o First add lib and python directories to LD_LIBRARY_PATH and PYTHONPATH,
      respectively, by doing

      source setup.sh  (assuming a bash shell)

    o To build all programs do

      make

      This will first build lib/libtnm.so from the codes in src, then
      build all the programs in the current directory, linked against the
      shared library.


    o To run the program, first create a text file (default name=filelist.txt)
    containing a list of the ntuples to be analyzed, one filename per line.
    Then do

      ./%(name)s

    If you wish to specify a different file list, say datafile.list, do

      ./%(name)s datafile.list

    If you wish to change the name of the root output file, say
    datahist.root, do

       ./%(name)s datafile.list datahist.root

For details, please refer to the documentation at:

    https://twiki.cern.ch/twiki/bin/viewauth/CMS/TheNtupleMaker

Notes 1
-------
    1. Use
    outputFile of(cl.outputfile, ev)

    where "ev" is the eventBuffer, if you wish to skim events to the output
    file in addition to writing out histograms. The current event is written
    to the file using

    of.write(event-weight) 

    where "of" is the output file. If omitted, the event-weight is
    taken to be 1.

    2. Use
    of.count(cut-name, event-weight)
    
    to keep track, in the count histogram, of the number of events passing
    a given cut. If omitted, the event-weight is taken to be 1. If you want
    the counts in the count histogram to appear in a given order, specify
    the order, before entering the event loop, as in the example below
    
    of.count("NoCuts", 0)
    of.count("GoodEvent", 0)
    of.count("Vertex", 0)
    of.count("MET", 0)
    
Notes 2
-------
    By default, when an event is written to the output file, all variables are
    written. However, before the event loop, you can use

    ev.select(objectname)

    e.g.,

    ev.select("GenParticle")

    to declare that you intend to select objects of this type. The
    selection is done, within the event loop, using

    ev.select(objectname, index)

    e.g.,

    ev.select("GenParticle", 3),

    which specifies that object 3 of GenParticle is to be kept. 

    NB: If you declare your intention to select objects of a given type
        by calling select(objectname), but subsequently fail to select
        them using select(objectname, index) then no objects of this
        type will be kept!
'''
#------------------------------------------------------------------------------
def cmp(x, y):
    if len(y) < len(x):
        return -1
    elif len(y) == len(x):
        return 0
    else:
        return 1
#------------------------------------------------------------------------------
isvector = re.compile('(?<!std::)vector')
getvtype = re.compile('(?<=vector[<]).*(?=[>])')
#------------------------------------------------------------------------------
def main():
    print "\n\tmkanalyzer.py"

    # Decode command line

    argv = sys.argv[1:]
    argc = len(argv)
    if argc < 1: usage()

    filename = nameonly(argv[0])

    if argc > 1:
        varfilename = argv[1]
    else:
        varfilename = "variables.txt"
    if not os.path.exists(varfilename):
        print "mkanalyzer.py - can't find variable file: %s" % varfilename
        sys.exit(0)


    # Check for macro mode
    macroMode = argc > 2


    # Read variable names

    records = map(strip, open(varfilename, "r").readlines())

    # Get tree name(s)

    t = split(records[0])
    if lower(t[0]) == "tree:":
        treename = t[1]
    else:
        treename = "Events"
    start = 1
    for record in records[1:]:
        record = strip(record)
        if record == "": break
        t = split(record)
        if lower(t[0]) == "tree:":
            treename += " %s" % t[1]
            start += 1

    # --------------------------------------------------------------------
    # Done with header, so loop over branch names
    # and get list of potential struct names (first field of
    # varname.
    # --------------------------------------------------------------------
    records = records[start:]
    tokens = []
    tmpmap = {}
    for index in xrange(len(records)):
        record = records[index]
        if record == "": continue

        # split record into its fields
        # varname = variable name as determined by mkvariables.py

        tokens.append(split(record, '/'))

        # note: count may include name of leafcounter or "*"
        rtype, branchname, varname, count = tokens[-1]

        # varname should have the format
        # <objname>_<field-name>
        t = split(varname,'_')
        if len(t) > 1: # Need at least two fields for a struct
            key = t[0]
            if not tmpmap.has_key(key): tmpmap[key] = 0
            tmpmap[key] += 1

    # If we have at least two fields, we'll create a struct
    structname = {}
    for key in tmpmap.keys():
        if tmpmap[key] > 1:
            structname[key] = tmpmap[key]

    # --------------------------------------------------------------------
    # Loop over tokens
    # --------------------------------------------------------------------
    usednames = {}
    varmap    = {}
    vectormap = {}

    skipped = '' # variables that are skipped
    for index, (rtype, branchname, varname, count) in enumerate(tokens):

        # check if current variable is a leaf counter (flagged with an "*")
        # or contains the name of a leaf counter
        t = split(count)
        count = atoi(t[0]) # change type to an integer
        iscounter   = t[-1] == "*"
        
        if t[0] != t[-1]:
            countername = t[-1]
        else:
            countername = None

        if count > 1:
            from math import sqrt
            count = int(count + 5*sqrt(count))
            ii = count / 5
            count = (ii+1)*5
            
        # make sure names are unique. If they aren't bail!

        if varmap.has_key(varname):
            print "** error ** duplicate variable name %s; "\
            "please fix variables.txt by hand"
            sys.exit(0)

        # do something about annoying types

        if find(varname, '[') > -1 and count > 1:
            skipped += "%s[%d]\n" % (branchname, count)
            continue
        if find(lower(rtype), 'ref') > -1:
            skipped += "%s[%d]\n" % (branchname, count)
            continue

        if find(lower(rtype), 'lorentz') > -1:
            skipped += "%s[%d]\n" % (branchname, count)
            continue

        # special handling for Delphes
        #if find(varname, '_size') > -1:
        #   varname = 'n%s' % replace(varname, '_size', '')

        if rtype == "bool":
            rtype = "int"
        elif rtype == "long64":
            rtype = "long"
        elif rtype == "int32":
            rtype = "int"
        elif rtype == "uchar":
            rtype = "int"
        elif rtype == "uint":
            rtype = "int"			


        objname = ''
        fldname = ''
        # If this is a leaf counter, which happens to have the same name
        # as a struct, then just ignore for now
        if iscounter:
            pass
        else:            
            # Get object and field names
            t = split(varname,'_')
            if len(t) > 0:
                # we have at least two fields in varname
                key = t[0]
                if structname.has_key(key):

                    # This branch potentially belongs to a struct.
                    objname = key
                    # Make sure the count for this branch matches that
                    # of existing struct
                    if not usednames.has_key(objname):
                        usednames[objname] = count;

                    if usednames[objname] == count:
                        fldname = replace(varname, '%s_' % objname, '')
                    else:
                        objname = ''
                        fldname = ''
                    
        # update map for all variables
        varmap[varname] = [rtype, branchname, count, iscounter, countername]
        
        # vector types must have the same object name and a max count > 1
        if count > 1:               
            if fldname != "":

                # Make sure fldname is a valid	c++ name		
                if fldname[0] in ['0','1','2','3','4','5','6','7','8','9']:
                    fldname = 'f%s' % fldname

                if not vectormap.has_key(objname): vectormap[objname] = []	
                vectormap[objname].append((rtype, fldname, varname, count, countername))
                #print "%s.%s (%s)" % (objname, fldname, count)

    if skipped != "":
        open("variables_skipped.txt", "w").write(skipped)
        
    # Declare all variables
    keys = varmap.keys()
    keys.sort()
    declarevec= []
    declare   = []
    init      = []
    setb      = []
    addb      = []
    impl      = []
    choose    = []
    # first create counters
    counters = {}
    for index, varname in enumerate(keys):
        rtype, branchname, count, iscounter, countername = varmap[varname]
        if iscounter:
            #objname = varname[1:] # n<object-name>
            counters[varname] = branchname
            addb.append('  output->add("%s", \t%s);' % (branchname, varname))
    addb.append('')

    for index, varname in enumerate(keys):
        rtype, branchname, count, iscounter, countername = varmap[varname]

        if macroMode:

            if iscounter:
                impl.append('  countvalue& v%d = (*varmap)["%s"];'%\
                            (index, branchname))
                impl.append('  if ( v%d.count )' % index)
                impl.append('    %s = *v%d.count;' % (varname, index))
                impl.append('  else')
                impl.append('    %s = 0;' % varname)
                impl.append('')			

            elif count == 1:
                impl.append('  countvalue& v%d = (*varmap)["%s"];' %\
                            (index, branchname))

                impl.append('  if ( v%d.value )' % index)
                impl.append('    %s = *v%d.value;' % (varname, index))
                impl.append('  else')
                impl.append('    %s = 0;' % varname)
                impl.append('')
            else:
                # this is a vector
                impl.append('  countvalue& v%d = (*varmap)["%s"];' % \
                            (index, branchname))

                impl.append('  if ( v%d.value )' % index)
                impl.append('    {')
                impl.append('      %s.resize(*v%d.count);' % (varname, index))
                impl.append('      copy(v%d.value, v%d.value+*v%d.count, '\
                            '%s.begin());'% (index, index, index, varname))
                impl.append('    }')
                impl.append('  else')
                impl.append('    %s.clear();' % varname)
                impl.append('')

        choose.append('  choose["%s"]\t= DEFAULT;' % branchname)
        setb.append('  if ( choose["%s"] )'   % branchname)
        cmd = '    input->select("%s", \t%s);' % (branchname, varname)
        if len(cmd) < 75:
            setb.append(cmd)
        else:
            setb.append('    input->select("%s",' % branchname)
            setb.append('                   %s);' % varname)

        if count == 1:
            declare.append("  %s\t%s;" % (rtype, varname))

        else:
            # this is either a vector or a variable length array

            if find(rtype, 'vector') > -1:
                rtype = isvector.sub("std::vector", rtype)
                vtype = getvectype.findall(rtype)
                if len(vtype) == 0:
                    sys.exit("** error ** unable to extract type from %s for variable %s" % \
                                 (rtype, varname))
                vtype = vtype[0]
                
                declarevec.append("  %s\t%s;" % (rtype, varname))
                init.append("    %s\t= %s(%d, %s);" % \
                        (varname, rtype, count, vtype))
            else:
                declarevec.append("  std::vector<%s>\t%s;" % (rtype, varname))
                init.append("    %s\t= std::vector<%s>(%d,0);" % \
                            (varname, rtype, count))
                if countername == None:
                    sys.exit("** error ** array %s does not have a leafcounter name" % varname)
                objname = countername
                if not counters.has_key(objname):
                    sys.exit("** error ** need to add leafcounter %s to variables.txt" % objname)
                branchname += "[%s]" % counters[objname]

        if not iscounter:
            cmd = '  output->add("%s", \t%s);' % (branchname, varname)
            if len(cmd) < 75:
                addb.append(cmd)
            else:            
                addb.append('  output->add("%s",' % branchname)
                addb.append('               %s);' % varname)

    # Create structs for vector variables

    pragma = []
    keys = vectormap.keys()
    keys.sort()
    structvec  = []	
    structdecl = []
    structimpl = []
    structimplall = []

    selectdecl = []
    selectimpl = []

    selectimpl.append('  // Save objects for which the select'\
                      ' function was called')
    selectimpl.append('  void saveObjects()')
    selectimpl.append('  {')
    if len(keys) > 0:
        selectimpl.append('    int n = 0;')
    structimplall.append('  void fillObjects()')
    structimplall.append('  {')

    for index, objname in enumerate(keys):
        values = vectormap[objname]
        varname= values[0][-3]

        structimplall.append('    fill%ss();' % objname)
        structimpl.append('  void fill%ss()' % objname)
        structimpl.append('  {')
        structimpl.append('    %s.resize(%s.size());' % (objname, varname))
        structimpl.append('    for(unsigned int i=0; i < %s.size(); ++i)' % \
                          objname)
        structimpl.append('      {')

        selectimpl.append('')
        selectimpl.append('    n = 0;')
        selectimpl.append('    try')
        selectimpl.append('      {')
        selectimpl.append('         n = indexmap["%s"].size();' % objname)
        selectimpl.append('      }')
        selectimpl.append('    catch (...)')
        selectimpl.append('      {}')
        selectimpl.append('    if ( n > 0 )')
        selectimpl.append('      {')
        selectimpl.append('        std::vector<int>& '\
                          'index = indexmap["%s"];' % objname)
        selectimpl.append('        for(int i=0; i < n; ++i)')
        selectimpl.append('          {')
        selectimpl.append('            int j = index[i];')
        structdecl.append('  struct %s_s' % objname)
        structdecl.append('  {')

        for rtype, fldname, varname, count, countername in values:
            # treat bools as ints
            if rtype == "bool":
                cast = '(bool)'
            else:
                cast = ''
            # this is a vector

            structdecl.append('    %s\t%s;' % (rtype, fldname))

            structimpl.append('        %s[i].%s\t= %s%s[i];' % (objname,
                                                              fldname,
                                                              cast,
                                                              varname))

            selectimpl.append('            %s[i]\t= %s[j];' % (varname, varname))

        structvec.append('  std::vector<eventBuffer::%s_s> %s;' % \
                             (objname, objname))
        init.append('    %s\t= std::vector<eventBuffer::%s_s>(%d);' % (objname,
                                                                       objname,
                                                                       count))
        pragma.append('#pragma link C++ class eventBuffer::%s_s;' % objname)
        pragma.append('#pragma link C++ class vector<eventBuffer::%s_s>;' % \
                          objname)
        pragma.append('')

        structdecl.append('')		
        structdecl.append('    std::ostream& operator<<(std::ostream& os)')
        structdecl.append('    {')
        structdecl.append('      char r[1024];')
        structdecl.append('      os << "%s" << std::endl;' % objname)

        for rtype, fldname, varname, count, countername in values:
            structdecl.append('      sprintf(r, "  %s: %s\\n", "%s",'\
                              ' ( double)%s); '\
                              'os << r;' % ("%-32s", "%f", fldname, fldname))
        structdecl.append('      return os;')
        structdecl.append('    }')
        structdecl.append('  };\n')
        
        structimpl.append('      }')
        structimpl.append('  }\n')  # end of fill<object>s()
        selectimpl.append('          }')
        selectimpl.append('      }')
        selectimpl.append('    %s = n;' % countername)
    structimplall.append('  }')  # end of fillObjects()
    selectimpl.append('  }')  # end of saveObjects()

    # Write out files

    if macroMode:

        names = {'NAME': upper(filename),
                 'name': filename,
                 'time': ctime(),
                 'author': AUTHOR,
                 'vardecl': join("", declare, "\n"),
                 'selection': join("  ", select, "\n"),
                 'structdecl': join("", structdecl, "\n"),
                 'structimpl': join("", structimpl, "\n"),
                 'structimplall': join("", structimplall, "\n"),
                 'selectimpl': join("", selectimpl, "\n"),
                 'impl': join("", impl, "\n"),
                 'treename': treename,
                 'percent': '%' }

        record = MACRO_DECL_H % names
        outfilename = "%s_decl.h" % filename
        open(outfilename, "w").write(record)

        record = MACRO_IMPL_H % names
        outfilename = "%s_impl.h" % filename
        open(outfilename, "w").write(record)
        sys.exit(0)

    # Put everything into a directory

    cmd = '''
    mkdir -p %(dir)s/tmp
    mkdir -p %(dir)s/lib
    mkdir -p %(dir)s/src
    mkdir -p %(dir)s/python
    mkdir -p %(dir)s/include
    cp %(hpp)s %(dir)s/include
    cp %(cpp)s %(dir)s/src
    ''' % {'dir': filename,
           'hpp': TREESTREAM_HPP,
           'cpp': TREESTREAM_CPP}
    os.system(cmd)

    cmd = '''
    cp %(hpp)s %(dir)s/include
    cp %(cpp)s %(dir)s/src
    cp %(py)s  %(dir)s/python
    ''' % {'dir': filename,
           'hpp': TNM_HPP,
           'cpp': TNM_CPP,
           'py' : TNM_PY
           }
    os.system(cmd)
    
    
    # Create Makefile

    names = {'name': filename,
             'filename': filename,
             'time': ctime(),
             'author': AUTHOR,
             'percent': '%'
             }

    record = MAKEFILE % names
    open("%s/Makefile" % filename, "w").write(record)	

    # Create C++ code

    declarevec += [""] + declare
    names = {'NAME': upper(filename),
             'name': filename,
             'time': ctime(),
             'author': AUTHOR,
             'vardecl':    join("", declarevec, "\n"),
             'init':       join("", init, "\n"),
             'setb':       join("  ", setb, "\n"),
             'choose':     join("  ", choose, "\n"),
             'addb':       join("  ", addb, "\n"),
             'structdecl': join("", structdecl, "\n"),
             'structimpl': join("", structimpl, "\n"),
             'structimplall': join("", structimplall, "\n"),
             'selectimpl': join("", selectimpl, "\n"),
             'structvec':    join("", structvec, "\n"),
             'treename': treename,
             'percent': '%' }

    record = TEMPLATE_H % names
    outfilename = "%s/include/eventBuffer.h" % filename
    open(outfilename,"w").write(record)

    # Create cc file if one does not yet exist
    outfilename = "%s/%s.cc" % (filename, filename)
    if not os.path.exists(outfilename):
        record = TEMPLATE_CC % names
        open(outfilename,"w").write(record)

    # Create README
    outfilename = "%s/README" % filename
    record = README % names
    open(outfilename,"w").write(record)

    # write out linkdef
    outfilename = "%s/include/linkdef.h" % filename
    names['pragma'] = join("", pragma, "\n")       
    record = LINKDEF % names
    open(outfilename,"w").write(record)
    
    # write setup.sh
    record = '''
if [ "$PYTHONPATH" == "" ]; then
    export PYTHONPATH=$PWD/python
else
    export PYTHONPATH=$PWD/python:$PYTHONPATH
fi

if [ "$LD_LIBRARY_PATH" == "" ]; then
    export LD_LIBRARY_PATH=$PWD/lib
else
    export LD_LIBRARY_PATH=$PWD/lib:$LD_LIBRARY_PATH
fi
'''
    outfilename = "%s/setup.sh" % filename
    open(outfilename,"w").write(record)

    # Create python program if one does not yet exist

    outfilename = "%s/%s.py" % (filename, filename)
    if not os.path.exists(outfilename):
        record = PYTEMPLATE % names
        open(outfilename,"w").write(record)
        os.system("chmod +x %s" % outfilename)

    print "\tcreated analysis directory: %s" % filename
    print "\n\tdo"
    print "\t\tcd %s" % filename
    print "\t\tmake"
    print "\n\tto build shared library libtnm.so\n"
#------------------------------------------------------------------------------
main()

