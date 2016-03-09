# multiple-dice-results

How to find the probability distribution of rolling a large number of dice? And how to do it efficiently?

This project started when I read the [post](http://www.tizona-sci.com/2011/07/case-study-fast-scripts-for.html) on that topic written by my friend [Francisco](http://blancosilva.github.io). Just as a side note: lots of great reading about scientific computing and Python on his websites, and not just for the beginners.

The problem is not hard mathematically, but it involves arbitrarily large integers, so arithmetic operations enter into complexity considerations. In particular, multiplications should probably be avoided in favor of additions and subtractions.

I had a lot of fun optimizing Francisco's solution in Python and C++.

### Python / Numpy / gmpy2
In general, either Python long type can be used, or a faster gmpy2 library based on gmp.

There is a rather slow one line solution using numpy polynomial power.

It seems better to keep convolving with a list of ones (even compared to binary power computation method). The convolution requires only one addition and one subtraction to find the next number, and only one half needs to be computed.

Just for fun, I have also developed a generator and deque based solutions (may need higher recursion limit). The overhead is not so big and the generator is actually faster when looking for not so large sums. As an added bouns, this approach could be used to convolve an infinite generator with a finite list of ones.

Functions in `dice.py`:
* `dice_polypow`, `dice_polypow_gmpy2`: Python long and gmpy2 one-liner solutions in numpy. Effectively iteration of convolutions.
* `dice_squaring`, `dice_squaring_gmpy2`: Power by squaring and numpy convolutions. Much slower than the first option.
* `dice`, `dice_gmpy2`: Pure Python solutions, but with convolution calculated in an optimal way (1 addition and 1 subtraction).
* `dice_numpy`: Same as above, but numpy `dtype=object` arrays used to avoid looping in Python. This is fastest. Although the benefit of numpy is small in terms of speed, but large in terms of the convenience of arithmetic operations on slices.
* `dice_deque_generator` (and helper function `convolve_deque`): Generator using deque to avoid indexing.

The file ends with a testing code.

### C++ / OpenMP
Here we can use gmp directly to handle arbitrary precision integers. As an added bonus it is possible to parallelize the code using a few OpenMP pragmas. However, the code needs to change significantly. A good parallel prefix sum implementation is needed. And another loop needs to be split into subloops with looping variable advancing by the number of faces, to make the subloops independent.

Files:
* `dice.cpp`: C++ version of the pure Python implementation. Not surprisingly it is faster, but only only less than twice.
* `diceomp.cpp`: Parallelized OpenMP version. Even with just 2 threads, this version is faster. Although the difference cannot be significant, since parallel prefix sums require 1.5x additions with 2 threads ((2-1/k)x with k threads). 

These can be tested with `test_c` and `timeit.sh` scripts.

### Running times
* All tests with 100-sided dice. 
* Fastest out of many runs reported.
* CPU: 4-core with hyperthreading. 
* 2 threads forced by OMP_NUM_THREADS

##### 128 rolls
The slowest, power by squaring methods. Even 128 rolls is a lot. And a power of 2 is the best for these:
* `dice_squaring`: 132.8 s
* `dice_squaring_gmpy2`: 75.9 s

##### 500 rolls
The one-liners are faster:
* `dice_polypow`: 187.2 s
* `dice_polypow_gmpy2`: 187.0 s

##### 1000 rolls
Python:
* `dice`: 18.08 s
* `dice_gmpy2`: 13.47 s
* `dice_numpy`: 11.39 s
* `dice_deque_generator`: 22.46 s

C++:
* `dice.cpp`: 6.95s
* `diceomp.cpp` (2 threads): 6.69 s
* `diceomp.cpp` (8 threads): 2.42 s

##### 2000 rolls
* `dice_numpy`: 103.70 s
* `dice_gmpy2`: 98.25 s
* `dice.cpp`: 54.79 s
* `diceomp.cpp` (2 threads): 39.68 s
* `diceomp.cpp` (8 threads): 17.16 s

