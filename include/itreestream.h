#ifndef ITREESTREAM_H
#define ITREESTREAM_H
//----------------------------------------------------------------------------
// File: itreestream.h
//
// Description: See treestream.h.
//
// Created: 23-Sep-2018 Harrison B. Prosper
//                      split treestream.h into two header files
//----------------------------------------------------------------------------
#include "Field.h"

/** Model an input stream of Root trees.
              The classes itreestream and otreestream provide a convenient 
              interface to the kind of Root trees typically used in HEP
              analyses.  Our (default) assumption is that there is one tree 
              per Root file and the objects stored are simple types. The
              treestream classes hide the boilerplate code for getting at 
              the tree, its branches and leaves.

              The design is based on the observation that, ultimately, data
              reduce to a set of name/value pairs in which the value 
              can be regarded as a homogeneous sequence of doubles, floats 
              longs, or ints. Moreover, an arbitrarily complex graph of the 
              name/value pairs is readily achieved with, well, name/value 
              pairs! Name/value pair is just another name for variable.
 
              Thinking in terms of objects, in the context of high energy 
              physics analysis, has yielded undue complexity. On the other 
              hand, thinking in terms of name/value pairs reduces the 
              complexity considerably. The irreducible complexity, which 
              surely exists, properly resides in the graph generated by 
              the set of variables.

              Of course, it is often convenient to package name/value pairs 
              into objects to avail oneself of some interesting behaviour. 
              This 
              may be useful, for example, to model a particularly 
              complicated sub-graph of variables. Or it may be that
              one wishes to take advantage of an object that defines
              useful functions on the variables. A  nice example of 
              packaging name/value pairs for this reason is the packaging 
              of the name/value pairs, Px, Py, Pz and E into 
              <i>TLorentzVector</i> objects to take advantage of the host of 
              useful mathematical operations these objects define on them.
*/
class itreestream
{
 public:

  ///
  itreestream();

  /** Create an input stream of trees.
      The default assumption is that the file contains a single kind of tree.
      If the file contains multiple trees, you should supply the tree name.
      <p>
      Note: <i>filename</i> is a string of one of more filenames, each of
      which can have wildcard characters.
  */
  itreestream(std::string filename, std::string treename="", int bufsize=1000);

  ///
  itreestream(std::vector<std::string>& filenames, std::string treename="",
              int bufsize=1000);

  ///
  virtual ~itreestream();

  ///
  void   init(TTree*);

  /// True if all is well.
  bool   good();

  /// Return status code.
  int    status();

  /// Check if given variable is present.
  bool   present(std::string name);

  ///
  void   select(std::string namen);

  ///
  void   select(std::vector<std::string>& namen);


  /** Specify the name of a variable to be read and give the address
      to which its value is to be written.
      <p>
      Note: The type of the buffer need not match that of the variable.
  */
  void   select(std::string namen, double& datum);

  ///
  void   select(std::string namen, float& datum);

  ///
  void   select(std::string namen, long& datum);

  ///
  void   select(std::string namen, int& datum);

  ///
  void   select(std::string namen, short& datum);

  ///
  void   select(std::string namen, bool& datum);

  ///
  void   select(std::string namen, unsigned long& datum);

  ///
  void   select(std::string namen, unsigned int& datum);

  ///
  void   select(std::string namen, unsigned short& datum);

  ///
  void   select(std::string namen, std::string& datum);

  /** Specify the name of a vector-valued variable to be read and give the
      address of a buffer into which its values are to be written. 
      The size of the (vector) buffer determines the maximum number of elements
      of the variable to read. You can check that all is well by
      calling the good() method after a call to select. The most likely
      error is failure to provide a buffer of non-zero length.
      <br>
      <b>Note</b>: The type of the buffer need not match that of the variable.
  */
  void   select(std::string namen, std::vector<double>& data);

  ///
  void   select(std::string namen, std::vector<float>& data);

  ///
  void   select(std::string namen, std::vector<long>& data);

  ///
  void   select(std::string namen, std::vector<int>& data);

  ///
  void   select(std::string namen, std::vector<short>& data);

  ///
  void   select(std::string namen, std::vector<bool>& data);

  ///
  void   select(std::string namen, std::vector<char>& data);

  ///
  void   select(std::string namen, std::vector<unsigned long>& data);

  ///
  void   select(std::string namen, std::vector<unsigned int>& data);

  ///
  void   select(std::string namen, std::vector<unsigned short>& data);

  /** Read tree with ordinal value <i>entry</i>. 
      Return the ordinal value of the
      entry within the current tree.
  */
  int    read(int entry);

  ///
  void   close();

  /// Return number of entries in stream.
  int    entries();

  /// Proxy for entries.
  int    size();

  /// Return the maxium size of name/value pair.
  int    maximum(std::string name);

  /// Return tree identifier.
  std::string  name();
 
  /// Return tree title.
  std::string  title();

  /// Return tree number. This may be useful when we have a chain of files.
  int          number();

  /// Return name of current file.
  std::string  filename();

  /// Return file names.
  std::vector<std::string> filenames();

  /// Return names of name/value pairs.
  std::vector<std::string> names();

  /// Return names of trees.
  std::vector<std::string> treenames();

  ///
  std::vector<double> vget();

  ///
  double get(std::string namen);

  ///
  std::string str() const;

  /// Print information about name/value pairs.
  void   ls(std::ostream& out=std::cout) { out << str(); }

//   /// Proxy for read.
//   int    operator[](int entry);

  ///
  TTree* tree();

  TFile* file();

 private:

  TTree*  _tree;
  TChain* _chain;
  int     _statuscode;
  int     _current;
  int     _entries;
  int     _entry;
  int     _index;
  std::vector<double> _buffer;

  Data          data;
  SelectedData  selecteddata;
  
  std::map<std::string, TChain*> _chainmap;
  
  int     _bufoffset;
  int     _bufcount;
  
  std::map<std::string, int> _bufmap;
  std::vector<std::string>  branchname;
  std::vector<int>          branchtab;
  std::vector<std::string>  filepath;

  void _open(std::vector<std::string>& filenames, 
             std::vector<std::string>& treenames);
  void _getbranches(TBranch* branch, int depth);
  void _getleaf    (TBranch* branch, TLeaf* leaf=0);
  void _select     (std::string name, void* address, int maxsize, 
                    char srctype, bool isvector=false);
  void _update();
  void _gettree(TDirectory* dir, int depth=0, std::string name="");

  bool _delete;
  std::string _treename;
  std::vector<std::string>  _treenames;
};

std::ostream& operator<<(std::ostream& os, const itreestream& tuple);

#endif
