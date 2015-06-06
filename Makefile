# Build libtreestream.so
# Created 27 Feb 2013 HBP & SS
#         30 May 2015 HBP - standardize structure (src, lib, include) 
# ----------------------------------------------------------------------------
ifndef ROOTSYS
	$(error *** Please set up Root compiled with RooFit/RooStats)
endif

ifndef EXTERNAL
$(error *** define EXTERNAL = to location of your bin, lib, and include directories)
endif
# ----------------------------------------------------------------------------
NAME	:= treestream
incdir	:= include
srcdir	:= src
libdir	:= lib
bindir	:= bin
$(shell mkdir -p lib; mkdir -p tmp)

# get lists of sources

SRCS	:=  	$(srcdir)/treestream.cc \
		$(srcdir)/pdg.cc

CINTSRCS:= $(wildcard $(srcdir)/*_dict.cc)

OTHERSRCS:= $(filter-out $(CINTSRCS) $(SRCS),$(wildcard $(srcdir)/*.cc))

# list of dictionaries to be created
DICTIONARIES	:= $(SRCS:.cc=_dict.cc)

# get list of objects
OBJECTS		:= $(SRCS:.cc=.o) $(OTHERSRCS:.cc=.o) $(DICTIONARIES:.cc=.o)

#say := $(shell echo "DICTIONARIES:     $(DICTIONARIES)" >& 2)
#say := $(shell echo "" >& 2)
#say := $(shell echo "SRCS: $(SRCS)" >& 2)
#say := $(shell echo "OBJECTS: $(OBJECTS)" >& 2)
#$(error bye)
# ----------------------------------------------------------------------------
ROOTCINT	:= rootcint
ifeq ($(shell which clang++),clang++)
CXX		:= clang++
LD		:= clang++
else
CXX		:= g++
LD		:= g++
endif
CPPFLAGS	:= -I. -I$(incdir)
CXXFLAGS	:= -O -Wall -fPIC -g -ansi -Wshadow -Wextra \
$(shell root-config --cflags)
LDFLAGS		:= -g
# ----------------------------------------------------------------------------
# which operating system?
OS := $(shell uname -s)
ifeq ($(OS),Darwin)
	LDFLAGS += -dynamiclib
	LDEXT	:= .dylib
else
	LDFLAGS	+= -shared
	LDEXT	:= .so
endif	
LDFLAGS += $(shell root-config --ldflags)
LIBS 	:= -lPyROOT $(shell root-config --libs --nonew)
# ----------------------------------------------------------------------------
all: lib$(NAME)$(LDEXT)

install:
	cp $(bindir)/mk*.py $(EXTERNAL)/bin
	cp $(incdir)/treestream.h $(EXTERNAL)/include
	cp $(incdir)/pdg.h $(EXTERNAL)/include
	cp $(libdir)/lib$(NAME)$(LDEXT) $(EXTERNAL)/lib
	find $(libdir) -name "*.pcm" -exec cp {} $(EXTERNAL)/lib \;

lib$(NAME)$(LDEXT)	: $(OBJECTS)
	@echo ""
	@echo "=> Linking shared library $@"
	$(LD) $(LDFLAGS) $^ $(LIBS)  -o $(libdir)/$@

$(OBJECTS)	: %.o	: 	%.cc
	@echo ""
	@echo "=> Compiling $<"
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@

$(DICTIONARIES)	: $(srcdir)/%_dict.cc	: $(incdir)/%.h $(srcdir)/%_linkdef.h
	@echo ""
	@echo "=> Building dictionary $@"
	$(ROOTCINT)	-f $@ -c $(CPPFLAGS) $^
	find $(srcdir) -name "*.pcm" -exec mv {} $(libdir) \;

tidy:
	rm -rf $(srcdir)/*_dict*.* $(srcdir)/*.o 

clean:
	rm -rf $(libdir)/* $(srcdir)/*_dict*.* $(srcdir)/*.o
	rm -rf $(EXTERNAL)/lib/*$(NAME)*
	rm -rf $(EXTERNAL)/lib/pdg_*.pcm
	rm -rf $(EXTERNAL)/include/*$(NAME)*
	rm -rf $(EXTERNAL)/include/pdg.h