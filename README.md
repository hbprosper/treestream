treestream
=======
A simple interface to Root files containing simple trees. We recommend
that you create a directory called __external__ in your home directory,
as shown below to contain all external packages, and install
__treestream__ in that directory.  You must 
define the *environment*  variable __EXTERNAL__, which must point to the
directory in which  __treestream__ has been installed. Assuming you
have installed this package in __external__ as recommended, do 

	export EXTERNAL=$HOME/external

You may wish to add this command to your __.bash_profile__, which is a hidden
file in your home directory. The above command is given for a bash shell.

INSTALLATION

	cd
	mkdir -p external/bin
	mkdir -p external/lib
	mkdir -p external/include

	git http://github.com/hbprosper/treestream.git
	cd external
	make
	make install

TEST

	cd test
	python testtreestream.py

ANALYZER UTILITIES

1. mkvariables.py reads a Root file and creates the file variables.txt 
containing a description of (by default) the first tree it finds.

2. mkanalyzer.py reads variables.txt and creates the skeleton of an C++ 
and Python analyzer program for the Root tree.
