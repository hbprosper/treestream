//----------------------------------------------------------------------------
// File: testtreestream.cc
// Description:
//  
// Writing code to create and and read flat ROOT ntuples (ones that store the
// standard types, int, long, float, double, string and arrays thereof) is a
// routine task. It is so routine in fact that this chore ought to be done
// for you...by a machine. That is the purpose of the package treestream. It
// handles all the boilerplate ROOT code for creating and reading flat ROOT
// ntuples and does so through a very simple interface. treestream is the
// modern incarnation of a package written in 2001 when the author finally
// got fed up of writing the same boilerplate code to create and read flat
// ntuples.
// 
// The package contains two classes itreestream and otreestream that can
// be called from C++ or Python (via PyROOT). This example shows how to
// use them.
//
// Created: 20-Sep-2018 Harrison B. Prosper
//----------------------------------------------------------------------------
#include <ctime>
#include <iomanip>
#include "TRandom3.h"
#include "treestream.h"
using namespace std;
//----------------------------------------------------------------------------
void write_ntuple(string filename="test.root", string treename="Events")
{
  time_t t = time(0);
  otreestream stream(filename, treename, ctime(&t));

  double HT = 0;
  int njet  = 0;
  vector<double> jetet(20);
  string comment(80, ' ');

  stream.add("HT", HT);  
  stream.add("njet", njet);
  stream.add("jetEt[njet]", jetet);
  stream.add("comment", comment);
  
  TRandom3 rand;
  int entries = 1000;
  int step    =  200;

  for(int entry=0; entry < entries; entry++)
    {
      njet = rand.Integer(10);
      jetet.clear();
      HT = 0.0;
      for(int i=0; i < njet; i++)
	{
	  jetet.push_back(rand.Exp(10));
	  HT += jetet.back();
	}

      char rec[80];
      sprintf(rec, "event: %5d njet = %2d", entry + 1, njet);
      comment = string(rec);
 
      stream.commit();

      if ( entry % step == 0 )
	{
	  cout << setw(5) << entry 
	       << setw(5) << jetet.size()  
	       << setw(10)<< HT
	       << " (" << comment << ")"
	       << endl;
	}
    }
  stream.close();
}
//----------------------------------------------------------------------------
void read_ntuple(string filename="test.root", string treename="Events")
{
  itreestream stream(filename, treename);
  
  int entries = stream.entries();
  stream.ls();

  double HT;
  vector<float> jetet(20);
  string comment(80, ' ');

  stream.select("jetEt", jetet);
  stream.select("comment", comment);
  stream.select("HT", HT);

  int step = 200;
  for(int entry=0; entry < entries; entry++)
    {
      stream.read(entry);

      if ( entry % step == 0 )
        cout << setw(5) << entry 
             << setw(5) << jetet.size()  
             << setw(10)<< HT
             << " (" << comment << ")"
             << endl;
    }
  stream.close();
}
//----------------------------------------------------------------------------
int main()
{
  cout << "treestream: read/write test" << endl;
  write_ntuple();
  read_ntuple();
  return 0;
}
