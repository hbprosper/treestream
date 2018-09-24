#ifndef TESTME_H
#define TESTME_H
//----------------------------------------------------------------------------
// File: testme.h
// Created: 20-Sep-2019 Harrison B. Prosper, test stuff
//----------------------------------------------------------------------------
#include <string>
#include <iostream>
#include <typeinfo>

struct testme
{
  testme() {}
  ~testme() {}

  template <typename T>
  void show(std::string comment, T& x)
  {
    std::string name(typeid(x).name());
    std::cout << comment
	      << "\t(" << name << ")"
	      << "\t(" << &x << ")"
	      << "\t(" << x << ")"
	      << std::endl;
  } 
};

template void testme::show(std::string, short&);
template void testme::show(std::string, int&);
template void testme::show(std::string, long&);
template void testme::show(std::string, unsigned short&);
template void testme::show(std::string, unsigned int&);
template void testme::show(std::string, float&);
template void testme::show(std::string, double&);
template void testme::show(std::string, std::string&);

#endif
