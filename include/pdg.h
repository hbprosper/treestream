#ifndef PDG_H
#define PDG_H
// -*- C++ -*-
//
// Package:    PhysicsTools
/**
   PhysicsTools/TheNtupleMaker/src/pdg.cc

 Description: A standalone implementation of some simple gen-particle utilities
 
 Implementation:
     As simple as possible
*/
//
// Original Author:  Harrison B. Prosper
//         Created:  Fri Apr 04 2008
// $Id: pdg.h,v 1.2 2013/07/11 01:54:22 prosper Exp $
//
//-----------------------------------------------------------------------------
#include <iostream>
#include <vector>
#include <string>
//-----------------------------------------------------------------------------
///
struct pdg
{
  ///
  static
  std::string particleName(int pdgid);


  ///
  static
  void printTree(std::ostream& stream,
                 int    index,
                 int    nhep,
                 std::vector<int>& pdgid,
                 std::vector<int>& status,
                 std::vector<float>& pt,
                 std::vector<float>& eta,
                 std::vector<float>& phi,
                 std::vector<float>& mass,
                 std::vector<int>& firstDaughter,
                 std::vector<int>& lastDaughter,
                 
                 int           printlevel=1,
                 int           maxdepth=10,
                 int           depth=0);

 ///
  static
  void printTree(std::ostream& stream,
                 int    index,
                 int    nhep,
                 std::vector<int>& pdgid,
                 std::vector<int>& status,
                 std::vector<double>& pt,
                 std::vector<double>& eta,
                 std::vector<double>& phi,
                 std::vector<double>& mass,
                 std::vector<int>& firstDaughter,
                 std::vector<int>& lastDaughter,
                 
                 int           printlevel=1,
                 int           maxdepth=10,
                 int           depth=0);

  ///
  static
  double deltaPhi(double phi1, double phi2);

  ///
  static
  double deltaR(double eta1, double phi1, double eta2, double phi2);
};
#endif
