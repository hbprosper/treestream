treestream
=======
A simple interface to Root files containing simple trees, such as the
CMS NanoAOD or the Root files created using __Delphes__. The enviroment variable __TREESTREAM_PREFIX__ should be set to the directory in which you wish to install treestream, that is, to the directory containing the bin, lib, and include directories. If you do not use an environment management system such as miniconda3 (a slim version of Anaconda), we suggest
that you create a directory called __external__ in your home directory,
as shown below to contain all external packages, and install
treestream in that directory.  You should clone (download) external packages to __external__, but do not try to install treestream within the treestream directory itself!

INSTALLATION
```bash
	cd
	mkdir -p external/bin
	mkdir -p external/lib
	mkdir -p external/include
	mkdir -p external/share

	cd $HOME/external
	git https://github.com/hbprosper/treestream.git
	cd treastream
	export TREESTREAM_PREFIX=$HOME/external (or $CONDA_PREFIX if you use miniconda3)
	make
	make install
```
TEST
```bash
	cd test
	./testtreestream
	./testdelphes
	./testvector
```
There is also a __jupyter__ notebook version of the test program.

ANALYZER UTILITIES

1. __mkvariables.py__  reads a Root file and creates the file __variables.txt__
containing a description of (by default) the first tree it finds.

2. __mkanalyzer.py__ reads __variables.txt__ and creates the skeleton of an C++ 
and Python analyzer program for the Root tree.
