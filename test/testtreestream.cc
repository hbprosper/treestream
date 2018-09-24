//----------------------------------------------------------------------------
// File: testtreestream.cc
//----------------------------------------------------------------------------
#include <iomanip>
#include "TRandom3.h"
#include "treestream.h"
using namespace std;
//----------------------------------------------------------------------------
int main()
{
  cout << "treestream: read/write test" << endl;

  otreestream oustream("test_cc.root", "Events", "Test");

  double ht = 0;
  int njet  = 0;
  vector<double> jetet(20);
  string astring(80, ' ');


  oustream.add("HT", ht);  
  oustream.add("njet", njet);
  oustream.add("jetEt[njet]", jetet);
  oustream.add("astring", astring);
  
  TRandom3 rand;
  int entries = 1400;
  int step    =  200;

  for(int entry=0; entry < entries; entry++)
    {
      njet = rand.Integer(10);
      jetet.clear();
      ht = 0.0;
      for(int i=0; i < njet; i++)
	{
	  jetet.push_back(rand.Exp(10));
	  ht += jetet.back();
	}

      char rec[80];
      sprintf(rec, "event: %5d njet = %2d", entry + 1, njet);
      astring = string(rec);
 
      oustream.commit();

      if ( entry % step == 0 )
	{
	  cout << setw(5) << entry 
	       << setw(5) << jetet.size()  
	       << setw(10)<< ht
	       << " (" << astring << ")"
	       << endl;
	}
    }
  oustream.close();

  // ----------------------------------------------------------------------------
  itreestream instream("test_cc.root", "Events");
  
  int ENTRIES = instream.entries();
  instream.ls();

  double HT;
  vector<float> JETET(20);
  string ASTRING(80, ' ');

  instream.select("jetEt", JETET);
  instream.select("astring", ASTRING);
  instream.select("HT", HT);
  
  for(int entry=0; entry < ENTRIES; entry++)
    {
      instream.read(entry);

      if ( entry % step == 0 )
        cout << setw(5) << entry 
             << setw(5) << JETET.size()  
             << setw(10)<< HT
             << " (" << ASTRING << ")"
             << endl;
    }

  instream.close();
  return 0;
}
