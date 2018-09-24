#ifndef FIELD_H
#define FIELD_H
//----------------------------------------------------------------------------
// File: Field.h
//
// Description: See treestream.h.
//
// Created: 23-Sep-2018 Harrison B. Prosper
//                      split Field.h from treestream.h
//----------------------------------------------------------------------------
#include <vector>
#include <string>
#include <list>
#include <map>
#include <sstream>
#include <iostream>
#include <typeinfo>
#include <cctype>


#include "TFile.h"
#include "TTree.h"
#include "TLeaf.h"
#include "TBranch.h"
#include "TChain.h"

/// Model a name/value pair.
struct Field
{
  Field() 
  : srctype(' '),
    iotype(' '),
    isvector(false),
    iscounter(false),
    maxsize(0),
    chain(0),
    branch(0),
    leaf(0),
    address(0),
    treename(""),
    branchname(""),
    leafname(""),
    fullname("")
  {}
  
  virtual ~Field() {}
  
  char   srctype;         /// Source type (type of user name/value pair)
  char   iotype;          /// Input/Output type
  bool   isvector;        /// True if vector type
  bool   iscounter;       /// true if this is a leaf counter
  int    maxsize;         /// Maximum number of elements in source variable

  TChain*  chain;         /// Chain to which this field is bound
  TBranch* branch;        /// Branch pertaining to source
  TLeaf*   leaf;          /// Leaf pertaining to source
  void*    address;       /// Source address

  std::string treename;   /// Tree name
  std::string branchname; /// Name of branch
  std::string leafname;   /// Name of T-leaf!
  std::string fullname;   /// Full name of branch/T-leaf!
};

template <class T>
struct FieldBuffer : public Field
{
  FieldBuffer() : Field(), value(std::vector<T>()) {}
  virtual ~FieldBuffer() {}
  
  std::vector<T> value;
};

typedef std::map<std::string, Field>  Data;
typedef std::map<std::string, Field*> SelectedData;

#endif
