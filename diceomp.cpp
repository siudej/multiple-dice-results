#include <iostream>
#include <cstdlib>
#include <gmpxx.h>
#include <omp.h>
#include <ctime>

using namespace std;

/*
void cumsum (int length, mpz_class *vec)
{
    int k;
    // Shift >>12 prevents divide and conquer from going too deep
    // Shift by 1 would be all the way.
    for (k=1; k<=length>>12; k<<=1)
#pragma omp parallel for shared(vec)
	for (int l=k-1; l<length-k; l+=2*k)
	    vec[l+k] += vec[l];
    // no parallel on shortest loops
    for (int l=k-1; l<length-k; l+=k)
	vec[l+k] += vec[l];
    for (k>>=1; k>0; k>>=1)
#pragma omp parallel for shared(vec)
	for (int l=2*k-1; l<length-k; l+=2*k)
	    vec[l+k] += vec[l];
}
*/

mpz_class* distribution(int faces, int num)
{
    mpz_class *vec = new mpz_class[(faces+(num-1)*(faces-1))/2+1];
    for (int i=0; i<faces; i++)
	vec[i] = i+1;
    int fmod = (faces+1) & 1;
    int length = faces;
    
    // helper definitions for parallel
    int max_chunks;
#pragma omp parallel
    max_chunks = omp_get_num_threads()+1;
    // chunks are for subarrays in cumsum
    // threads+1 is ok, since both passes use one less chunk
    mpz_class *ends = new mpz_class[max_chunks];
    ends[0] = 0;
    
    // convolve num times
    for (int i=2;i<num;i++)
    {	
	int e = fmod & i;
        int correction = - 2 + e;
        int added = (faces-1)/2 + e;
	// just assign to a few new spots, so no parallel
	for (int j=0; j<added; j++)
	    vec[j+length] = vec[length+correction-j];
	length += added;
	// if small length, then only 2 chunks
	int chunks = (length < 100*max_chunks) ? 2 : max_chunks;

#pragma omp parallel
    	{
	    
	    // split into sequences advancing by faces to make the chunks independent
#pragma omp for schedule(dynamic,1)
	    for (int k=0;k<faces;k++)
		for (int j=length-1-k; j>=faces; j-=faces)
		    vec[j] -= vec[j-faces];
	    
	    //
	    // parallel cumsum
	    //
	    // compute sums for subregions, except the last one
	    // first one already in place
#pragma omp for schedule(static)
	    for (int j=chunks-1; j>0;j--)
		if (j>1)
		{
		    mpz_class sum(0);
		    for (int k=(j-1)*length/chunks; k<j*length/chunks; k++)
			sum += vec[k];
		    ends[j] = sum;
		} 
		else 
		{
		    int k=0;
		    for (; k<length/chunks-1; k++)
			vec[k+1] += vec[k];
		    ends[1] = vec[k];
		}
	    // cumsum on computed sums and put in place
#pragma omp single
	    for (int j=1; j<chunks; j++)
	    {
		ends[j] += ends[j-1];
		vec[j*length/chunks] += ends[j];
	    }
	    // cumsum on subregions, except the first one
#pragma omp for schedule(static)
	    for (int j=chunks; j>1;j--)
		for (int k=(j-1)*length/chunks; k<j*length/chunks-1; k++)
		    vec[k+1] += vec[k];
    	}
    }
    delete [] ends;
    return vec;
}



int main(int argc, char **argv)
{
    int faces = atoi(argv[1]);
    int num = atoi(argv[2]);
    int length = (faces+(num-1)*(faces-1))/2+1;
    int i;
    mpz_class *vec = distribution(faces, num);
    mpz_class max(1);
    for (i=0; i<length; i++)
	if (max<vec[i])
	    max = vec[i];
    // homebrew g++-5 and gmp have a problem with cout<<mpz_class
    // cout<<max.get_str();
    delete [] vec;
}

