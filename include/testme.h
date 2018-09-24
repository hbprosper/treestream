#ifndef TESTME_H
#define TESTME_H
//----------------------------------------------------------------------------
// File: testme.h
// Created: 20-Sep-2019 Harrison B. Prosper, test stuff
//----------------------------------------------------------------------------
//#include <Python.h>
//#include <boost/python/type_id.hpp>
#include <vector>
#include <string>
#include <list>
#include <map>
#include <sstream>
#include <iostream>
#include <typeinfo>
#include <cctype>

struct testme
{
  testme() {}
  ~testme() {}

  template <typename T>
  void show(std::string comment, T& x)
  {
    //std::string name(boost::python::type_id<T>().name());
    std::string name(typeid(x).name());
    std::cout << comment
	      << "\t(" << name << ")"
	      << "\t(" << &x << ")"
	      << "\t(" << x << ")"
	      << std::endl;
  } 
  
  /* void show(std::string comment, int& x) */
  /* { */
  /*   show<int>(comment, x); */
  /* } */

  /* void show(std::string comment, long& x) */
  /* { */
  /*   show<long>(comment, x); */
  /* } */

  /* void show(std::string comment, unsigned int& x) */
  /* { */
  /*   show<unsigned int>(comment, x); */
  /* } */

  /* void show(std::string comment, float& x) */
  /* { */
  /*   show<float>(comment, x); */
  /* } */

  /* void show(std::string comment, double& x) */
  /* { */
  /*   show<double>(comment, x); */
  /* }   */
};

template void testme::show(std::string, short&);
template void testme::show(std::string, int&);
template void testme::show(std::string, long&);
template void testme::show(std::string, unsigned short&);
template void testme::show(std::string, unsigned int&);
//template void testme::show(std::string, unsigned long&);
template void testme::show(std::string, float&);
template void testme::show(std::string, double&);

#endif
