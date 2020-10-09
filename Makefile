# Build libtreestream.so
# Created 27 Feb 2013 HBP & SS
#         30 May 2015 HBP - standardize structure (src, lib, include) 
# ----------------------------------------------------------------------------
ifndef ROOTSYS
$(error *** Please set up Root)
endif

ifndef EXTERNAL
EXTERNAL:=.
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

#say := $(shell echo "DICTIONARIES:     $(DICTIONARIES)" >& 2)
#say := $(shell echo "" >& 2)
#say := $(shell echo "SRCS: $(SRCS)" >& 2)
#say := $(shell echo "TESTS: $(TESTS)" >& 2)
#$(error bye)
# ----------------------------------------------------------------------------
ROOTCINT	:= rootcint

# check for clang++, otherwise use g++
COMPILER	:= $(shell which clang++)
ifneq ($(COMPILER),)
CXX		:= clang++
LD		:= clang++
else
CXX		:= g++
LD		:= g++
endif
CPPFLAGS	:= -I. -I$(incdir) $(shell root-config --cflags)
CXXFLAGS	:= -c -g -O2 -ansi -O -Wall -pipe -fPIC
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
all: $(TESTS) $(LIBRARY)

ifdef EXTERNAL
install:
	cp $(bindir)/mk*.py $(EXTERNAL)/bin
	cp $(incdir)/treestream.h $(EXTERNAL)/include
	cp $(incdir)/pdg.h $(EXTERNAL)/include
	cp $(libdir)/lib$(NAME)$(LDEXT) $(EXTERNAL)/lib
	find $(libdir) -name "*.pcm" -exec mv {} $(EXTERNAL)/lib \;
endif

$(TESTS)	: %	:	%.o	$(LIBRARY)
	@echo ""
	@echo "=> Linking test program $@"
	$(LD) $(ROOTFLAGS) $^ -L$(libdir) -l$(NAME) $(LIBS) -o $@

$(OBJTESTS)	: %.o	:	%.cc
	@echo ""
	@echo "=> Compiling $<"
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@

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

tidy:
	rm -rf $(srcdir)/*_dict*.* $(srcdir)/*.o $(testdir)/*.o

clean:
	rm -rf $(libdir)/* $(srcdir)/*_dict*.* $(srcdir)/*.o
	rm -rf $(TESTS) $(OBJTESTS)
	rm -rf $(EXTERNAL)/lib/*$(NAME)*
	rm -rf $(EXTERNAL)/lib/pdg_*.pcm
	rm -rf $(EXTERNAL)/include/*$(NAME)*
	rm -rf $(EXTERNAL)/include/pdg.h
