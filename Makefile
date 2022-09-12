# Build libtreestream.so
# Created 27 Feb 2013 HBP & SS
#         30 May 2015 HBP - standardize structure (src, lib, include) 
# ----------------------------------------------------------------------------
ifndef ROOTSYS
$(error *** Please set up Root)
endif

ifndef TREESTREAM_PREFIX
TREESTREAM_PREFIX := $(CONDA_PREFIX)
endif
# ----------------------------------------------------------------------------
NAME	:= treestream
incdir	:= include
srcdir	:= src
libdir	:= lib
bindir	:= bin
testdir	:= test

SRCTESTS:= \
$(testdir)/testtreestream.cc \
$(testdir)/testdelphes.cc \
$(testdir)/testvector.cc

OBJTESTS:= $(SRCTESTS:.cc=.o)
TESTS	:= $(SRCTESTS:.cc=)

$(shell mkdir -p lib)

# get lists of sources

SRCS	:=  	$(srcdir)/treestream.cc \
		$(srcdir)/pdg.cc \
		$(srcdir)/testme.cc

CINTSRCS	:= $(wildcard $(srcdir)/*_dict.cc)

OTHERSRCS	:= $(filter-out $(CINTSRCS) $(SRCS),$(wildcard $(srcdir)/*.cc))

# list of dictionaries to be created
DICTIONARIES	:= $(SRCS:.cc=_dict.cc)

# get list of objects
OBJECTS		:= $(SRCS:.cc=.o) $(OTHERSRCS:.cc=.o) $(DICTIONARIES:.cc=.o)

PYTHONLIB	:= python$(shell python --version | cut -c 8-10)

#say := $(shell echo "DICTIONARIES:     $(DICTIONARIES)" >& 2)
#say := $(shell echo "" >& 2)
#say := $(shell echo "SRCS: $(SRCS)" >& 2)
#say := $(shell echo "PYTHON_LIB: $(PYTHONLIB)" >& 2)
#$(error bye)
# ----------------------------------------------------------------------------
ROOTCINT	:= rootcint

# check for clang++, otherwise use g++
COMPILER	:= $(shell which clang++)
ifneq ($(COMPILER),)
CXX		:= /usr/bin/clang++
LD		:= /usr/bin/clang++
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


LDFLAGS += $(ROOTFLAGS) -Wl,-rpath,$(ROOTSYS)/lib
LIBS 	:= $(shell root-config --libs)
LIBRARY	:= $(libdir)/lib$(NAME)$(LDEXT)
# ----------------------------------------------------------------------------
all: $(LIBRARY) $(TESTS)

ifdef TREESTREAM_PREFIX
install:
	cp $(bindir)/mk*.py $(TREESTREAM_PREFIX)/bin
	cp $(incdir)/treestream.h $(TREESTREAM_PREFIX)/include
	cp $(incdir)/pdg.h $(TREESTREAM_PREFIX)/include
	cp $(libdir)/lib$(NAME)$(LDEXT) $(TREESTREAM_PREFIX)/lib
	find $(libdir) -name "*.pcm" -exec mv {} $(TREESTREAM_PREFIX)/lib \;
	cp treestream.py $(TREESTREAM_PREFIX)/lib/$(PYTHONLIB)/site-packages
endif


$(LIBRARY)	: $(OBJECTS)
	@echo ""
	@echo "=> Linking shared library $@"
	$(LD) $(LDFLAGS) $^ $(LIBS)  -o $@

$(OBJECTS)	: %.o	: 	%.cc
	@echo ""
	@echo "=> Compiling $<"
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@

$(DICTIONARIES)	: $(srcdir)/%_dict.cc	: $(incdir)/%.h $(srcdir)/%_linkdef.h
	@echo ""
	@echo "=> Building dictionary $@"
	$(ROOTCINT)	-f $@ -c $(CPPFLAGS) $^
	find $(srcdir) -name "*.pcm" -exec mv {} $(libdir) \;


$(OBJTESTS)	: %.o	:	%.cc
	@echo ""
	@echo "=> Compiling $<"
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@


$(TESTS)	: %	:	%.o	$(LIBRARY)
	@echo ""
	@echo "=> Linking test program $@"
	$(LD) $(ROOTFLAGS) $^ -L$(libdir) -l$(NAME) $(LIBS) -o $@


tidy:
	rm -rf $(srcdir)/*_dict*.* $(srcdir)/*.o $(testdir)/*.o

clean:
	rm -rf $(libdir)/* $(srcdir)/*_dict*.* $(srcdir)/*.o
	rm -rf $(TESTS) $(OBJTESTS)
	rm -rf $(TREESTREAM_PREFIX)/lib/*$(NAME)*
	rm -rf $(TREESTREAM_PREFIX)/lib/pdg_*.pcm
	rm -rf $(TREESTREAM_PREFIX)/include/*$(NAME)*
	rm -rf $(TREESTREAM_PREFIX)/include/pdg.h
	rm -rf $(TREESTREAM_PREFIX)/lib/$(PYTHONLIB)/site-packages/$(NAME).py
