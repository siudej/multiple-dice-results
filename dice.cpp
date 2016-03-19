#include <iostream>
#include <gmpxx.h>
#include <vector>

using namespace std;

void distribution(int faces, int num, vector<mpz_class>& vec)
{
    int length = (faces+(num-1)*(faces-1))/2+1;
    vec.resize(length);
    for (int i=0; i<faces; i++)
	vec[i] = i+1;
    int fmod = (faces+1) & 1;
    length = faces;
    for (int i=2;i<num;i++)
    {	
	int e = fmod & i;
        int correction = - 2 + e;
        int added = (faces-1)/2 + e;
	for (int j=0; j<added; j++)
	    vec[j+length] = vec[length+correction-j];
	length += added;
	for (int j=length-1; j>=faces; j--)
	    vec[j] -= vec[j-faces];
	for (int j=1; j<length; j++)
	    vec[j] += vec[j-1];
    }
}


int main(int argc, char **argv)
{
    int faces = atoi(argv[1]);
    int num = atoi(argv[2]);
    vector<mpz_class> vec;
    distribution(faces, num, vec);
    mpz_class max(1);
    for (int i = 0; i != vec.size(); i++)
	if (max<vec[i])
	    max = vec[i];
    cout<<max<<endl;
}

