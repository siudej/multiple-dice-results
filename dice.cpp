#include <iostream>
#include <gmpxx.h>

using namespace std;

mpz_class* distribution(int faces, int num)
{
    int length = (faces+(num-1)*(faces-1))/2+1;
    mpz_class *vec = new mpz_class[length];
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
    return vec;
}


int main(int argc, char **argv)
{
    int faces = atoi(argv[1]);
    int num = atoi(argv[2]);
    int length = (faces+(num-1)*(faces-1))/2+1;
    mpz_class *vec = distribution(faces, num);
    mpz_class max(1);
    for (int i=0; i<length; i++)
	if (max<vec[i])
	    max = vec[i];
    //cout<<max;
    delete [] vec;
}

