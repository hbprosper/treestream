treestream
=======
A simple interface to Root files containing simple trees, such as the
CMS NanoAOD. We recommend
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
```bash
	cd
	mkdir -p external/bin
	mkdir -p external/lib
	mkdir -p external/include
	mkdir -p external/share

	git https://github.com/hbprosper/treestream.git
	cd external
	make
	make install
```
TEST
```bash
	cd test
	./testtreestream
	./testtreestream.py
```
There is also a __jupyter__ notebook version of the test program.

ANALYZER UTILITIES

1. __mkvariables.py__  reads a Root file and creates the file __variables.txt__
containing a description of (by default) the first tree it finds.

2. __mkanalyzer.py__ reads __variables.txt__ and creates the skeleton of an C++ 
and Python analyzer program for the Root tree.
