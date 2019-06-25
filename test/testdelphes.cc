// ----------------------------------------------------------------------------
// Test reading Delphes file
// created: 23-Jun-2019 HBP
// ----------------------------------------------------------------------------
#include <ctime>
#include <iomanip>
#include "treestream.h"
using namespace std;
// ----------------------------------------------------------------------------
int main()
{
  string filename("fatjet.root");
  string treename("Delphes");

  itreestream stream(filename, treename);

  printf("\n\tTest reading of variable length arrays\n");
  
  vector<float> PT(20);
  stream.select("Jet.PT", PT);

  vector<vector<float> > Tau(20);
  stream.select("FatJet.Tau[5]", Tau);
  
  int entries = stream.entries();
  cout << endl << "entries: " << entries << endl;
  
  for(int entry=0; entry < entries; entry++)
    {
      stream.read(entry);
      if ( Tau.size() < (size_t)1 ) continue;
      
      cout << endl << "event: " << entry << endl;
      
      printf("  PT.size(): %d\n", (int)PT.size());
      for(size_t ii=0; ii < PT.size(); ii++)
	printf("   %5d\t%10.2f\n", (int)ii, PT[ii]);

      printf("\n  Tau.size(): %d\n", (int)Tau.size());
      for(size_t ii=0; ii < Tau.size(); ii++)
  	{
  	  printf("   %5d\t%d\n", (int)ii, (int)Tau[ii].size());
	  for(size_t jj=0; jj < Tau[ii].size(); jj++)
	    printf("   %5d\t%10.2f\n", (int)jj, Tau[ii][jj]);
  	}      
    }
  
  return 0;
}

