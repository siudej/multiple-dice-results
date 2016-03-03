#!/usr/bin/env python
"""
Distribution of the sum of a large number of dice rolls.

Needs Python long type due to likely integer overflow.

Reduces to convolving a list of ones with itself many times.
"""
from numpy import array, cumsum, empty, copy
from numpy.polynomial import polynomial as P
from datetime import datetime
import sys
from collections import deque


# numpy implementation
def dice(faces, num):
    """ Use power of a polynomial as iterated convolution. """
    return P.polypow(array([1]*faces, dtype=object), num)


# much faster implementations
def dice2(faces, num):
    """
    Iterate convolutions.

    Only first half is needed, by symmetry.

    Convolution with ones only requires +new -old element to slide the window.
    """
    # space for the full output
    main = empty((faces+(num-1)*(faces-1))/2+1, dtype=object)
    # slice for a given iteration
    lst = main[:faces]
    lst[:] = range(1, faces+1)
    fmod = ((faces+1) % 2)
    for j in range(2, num):
        e = fmod * (j % 2)
        old = len(lst)
        temp = - 2 + e
        new = (faces-1)/2 + e
        # add a few elements past the half
        main[old:old+new] = lst[temp:temp-new:-1]
        # new length of the half
        lst = main[:old+new]
        # differences between consecutive sums: +new -old
        # overlapping slices prevent simple -=
        lst[faces:] -= copy(lst[:-faces])
        # accumulate to get sums
        cumsum(lst, out=lst)
    return lst


def dice3(faces, num):
    """ Iterate convolutions. """
    lst = range(1, faces+1)
    for i in range(2, num):
        # there is a double element sometimes
        e = ((faces+1) % 2) * (i % 2)
        lst = list(convolve_gen(lst, faces, e))
        # lst = list(convolve_deque(iter(lst), faces, (i+1) % 2))
    # e = ((faces+1) % 2) * (num % 2)
    # lst.extend(lst[-2+e::-1])
    return lst


def convolve_gen(lst, n, e):
    """
    Convolve a symmetric lst with n 1s.

    Only the first half as a generator.
    """
    res = 0
    old = len(lst)
    new = old + (n-1)/2 + e
    # first few shorter sums
    for i in range(n):
        res += lst[i]
        yield res
    # other sums using +new -old
    for i in range(n, old):
        res += lst[i]
        res -= lst[i-n]
        yield res
    # last few working backwards
    temp = old - 2 + e - n
    for i in range(old-n, new-n):
        res += lst[temp-i]
        res -= lst[i]
        yield res


def convolve_deque(gen, n, k):
    """ Convolve using deque. """
    q = deque()
    r = 0
    for _ in range(n):
        e = next(gen)
        q.append(e)
        r += e
        yield r
    for e in gen:
        r += e
        r -= q.popleft()
        q.append(e)
        yield r
    if (n % 2) + k:
        q.pop()
    while len(q) > 1:
        r += q.pop()
        r -= q.popleft()
        yield r


def dice4(faces, num):
    """ Generator version of dice. """
    gen = (i for i in xrange(1, faces+1))
    for i in range(3, num+1):
        gen = convolve_deque(gen, faces, i % 2)
    return gen

faces = 6
n = 4
print dice(faces, n)
print dice2(faces, n)
print dice3(faces, n)
print list(dice4(faces, n))

faces = 100
n = 1000
if n > 300:
    sys.setrecursionlimit(n*3)

# too slow with n = 1000
start = datetime.now()
print max(dice(faces, 200))
print datetime.now() - start

start = datetime.now()
print max(dice2(faces, n))
print datetime.now() - start

start = datetime.now()
print max(dice3(faces, n))
print datetime.now() - start

start = datetime.now()
print max(dice4(faces, n))
print datetime.now() - start

start = datetime.now()
gen = dice4(faces, n)
print max(gen.next() for _ in range(10000))
print datetime.now() - start
