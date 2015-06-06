treestream
=======
A simple interface to Root files containing simple trees.

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
