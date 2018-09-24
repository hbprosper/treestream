#ifndef OTREESTREAM_H
#define OTREESTREAM_H
//----------------------------------------------------------------------------
// File: otreestream.h
//
// Description: See treestream.h.
//
// Created: 23-Sep-2018 Harrison B. Prosper
//                      Split otreestream.h from treestream.h
//----------------------------------------------------------------------------
#include "Field.h"

/// Model an output stream of trees of the same species.
class otreestream
{
 public:
  
  otreestream();
  
  /// Create an output stream of trees.
  otreestream(std::string filename, 
              std::string treename, 
              std::string treetitle,
              int complevel=2,
              int bufsize=1000);
  
  /// Create an output stream of trees.
  otreestream(TFile* file,
              std::string treename, 
              std::string treetitle,
              int complevel=2,
              int bufsize=1000);
  
  virtual ~otreestream();

  ///
  bool   good();

  ///
  int    status();

  ///
  void   add(std::string namen, int& datum);
  
  ///
  void   add(std::string namen, unsigned int& datum);

  ///
  void   add(std::string namen, long& datum);

  ///
  //void   add(std::string namen, unsigned long& datum);
  
  ///
  void   add(std::string namen, short& datum);
  
  ///
  void   add(std::string namen, unsigned short& datum);

  ///
  //void   add(std::string namen, char& datum);

  ///
  void   add(std::string namen, bool& datum);

  /** Specify the name of a variable to be added to the tree and the address 
      from which its value is to be read. 
  */
  void   add(std::string namen, double& datum, char iotype='D');

  ///
  void   add(std::string namen, float& datum);

  ///
  void   add(std::string namen, std::string& datum);

  /** Specify the name of a variable to be added to the tree and and the 
      address from which its value is to be read. <p>Note: <i>name</i> 
      can have the form
      <name>[<countername>], e.g., JetEt[numberJet] if it is of variable
      length. Of course, the variable <i>numberJet</i> must be stored also! 
      For a variable of fixed length use e.g., 
      JetEt[10].
  */
  void   add(std::string namen, std::vector<long>& data);

  ///
  void   add(std::string namen, std::vector<int>& data);

  ///
  void   add(std::string namen, std::vector<short>& data);

  ///
  //void   add(std::string namen, std::vector<char>& data);

  ///
  void   add(std::string namen, std::vector<bool>& data);

  ///
  //void   add(std::string namen, std::vector<unsigned long>& data);

  ///
  void   add(std::string namen, std::vector<unsigned int>& data);

  ///
  void   add(std::string namen, std::vector<unsigned short>& data);

  ///
  void   add(std::string namen, std::vector<double>& data, char iotype='D');

  ///
  void   add(std::string namen, std::vector<float>& data);

  ///
  void   add(std::string namen);

  ///
  void   insert(std::vector<double>& data);

  /// Store values of all name/value pairs in output buffers.
  void   store();

  /// Save contents of output buffers.
  void   save();

  /// Store and save.
  void   commit();

  /// Automatically save the tree header after every Mbytes written to file.
  void   autosave(int Mbytes=-1);

  ///
  void   close(bool closefile=true);

  ///
  int    entries();

  ///
  int    size();

  /// Return tree identifier.
  std::string  name();
 
  ///
  std::string  title();

  ///
  std::vector<std::string> names();

  ///
  std::string str() const;

  ///
  void   ls(std::ostream& out=std::cout);

  ///
  TFile* file();

  ///
  TTree* tree();

 private:

  TFile* _file;
  TTree* _tree;
  int    _statuscode;
  int    _entries;
  int    _entry;
  int    _idatabuf;
  std::vector<double> _databuf;
  int    _autosavecount;

  std::map<std::string, Field*> selecteddata;

  std::vector<std::string>      branchname;
  std::vector<int*> strsize;

  void _add(std::string name, void* address, int maxsize,
	    char srctype, char iotype, bool isvector=false);
};

std::ostream& operator<<(std::ostream& os, const otreestream& tuple);

#endif
