#!/Users/siudeja/anaconda/bin/python
"""
Distribution of the sum of a large number of dice rolls.

Needs arbitrary precision integer type due to likely integer overflow.

Reduces to convolving a list of ones with itself many times.
"""
from numpy import array, convolve, empty, copy, cumsum
from numpy.polynomial import polynomial as P
from gmpy2 import mpz
from collections import deque
import timeit


def dice_polypow(faces, num):
    """ Numpy polynomial power function (iterated convolve). """
    return P.polypow(array([mpz(1)]*faces, dtype=object), num)


def dice_polypow_gmpy2(faces, num):
    """ Numpy polynomial power function (iterated convolve). With gmpy2. """
    return P.polypow(array([mpz(1)]*faces, dtype=object), num)


def dice_squaring(faces, num):
    """Polynomial power via squaring. This is actually much slower."""
    res = 1
    p = array([1]*faces, dtype=object)
    while num > 0:
        if num & 1:
            res = convolve(p, res)
        num >>= 1
        p = convolve(p, p)
    return res


def dice_squaring_gmpy2(faces, num):
    """Polynomial power via squaring and gmpy2. This is actually much slower."""
    res = 1
    p = array([mpz(1)]*faces, dtype=object)
    while num > 0:
        if num & 1:
            res = convolve(p, res)
        num >>= 1
        p = convolve(p, p)
    return res


#
# Optimized versions use iterated convolution with a sequence of ones.
# Entries of the convolution are sums of consecutive elements of the list,
# so to compute the next sum we do -first +new.
#
# No multiplication of long integers is used.
#


def dice(faces, num):
    """ Pure Python implementation with Python long type. """
    length = (faces+(num-1)*(faces-1))/2+1

    vec = [1]*length
    vec[:faces] = range(1, faces+1)

    fmod = (faces+1) & 1
    length = faces
    for i in range(2, num):
        e = fmod & i
        correction = - 2 + e
        added = (faces-1)/2 + e
        for j in range(0, added):
            vec[j+length] = vec[length+correction-j]
        length += added
        for j in range(length-1, faces-1, -1):
            vec[j] -= vec[j-faces]
        for j in range(1, length):
            vec[j] += vec[j-1]
    return vec


def dice_gmpy2(faces, num):
    """ Pure Python implementation with gmpy2. """
    length = (faces+(num-1)*(faces-1))/2+1

    # this is the only place where gmpy2 replaces Python long
    vec = [mpz(1)]*length
    vec[:faces] = [mpz(i) for i in range(1, faces+1)]

    fmod = (faces+1) & 1
    length = faces
    for i in range(2, num):
        e = fmod & i
        correction = - 2 + e
        added = (faces-1)/2 + e
        for j in range(0, added):
            vec[j+length] = vec[length+correction-j]
        length += added
        for j in range(length-1, faces-1, -1):
            vec[j] -= vec[j-faces]
        for j in range(1, length):
            vec[j] += vec[j-1]
    return vec


def dice_numpy(faces, num):
    """ Numpy object array instead of Python loops. """
    # space for the full output
    main = empty((faces+(num-1)*(faces-1))/2+1, dtype=object)
    # will hold the view for a given iteration
    lst = main[:faces]
    lst[:] = range(1, faces+1)
    # fmod and e (in the loop) determine whether there is a double element at
    # the end of the half
    fmod = (faces+1) & 1
    for j in range(2, num):
        e = fmod & j
        old = len(lst)
        correction = - 2 + e
        # number of new entries for the next iteration
        new = (faces-1)/2 + e
        # add a few elements past the old half taking care to add double element
        # if needed
        main[old:old+new] = lst[correction:correction-new:-1]
        # view for the new half
        lst = main[:old+new]
        # differences between consecutive sums: +new -old
        # overlapping slices prevent simple -=
        lst[faces:] -= copy(lst[:-faces])
        cumsum(lst, out=lst)
    return main


#
# gmpy2 in numpy array does not work, since cumsum produces strange results
# as if mpz was mutable and cumsum reuses objects
#


def convolve_deque(gen, n, k):
    """
    Convolve with ones using deque.

    In principle, could work on an infinite list.
    """
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


def dice_deque_generator(faces, num):
    """ Generator and deque version. """
    gen = (i for i in xrange(1, faces+1))
    for i in range(3, num+1):
        gen = convolve_deque(gen, faces, i % 2)
    return gen


def dice_gen(faces, num):
    """ Exhaust dice generator. """
    return list(dice_deque_generator(faces, num))

import sys
sys.setrecursionlimit(3000)


# list of functions to test
# the generator one needs to be exhausted, so the __doc__ cannot be accessed
funs = [dice_polypow, dice_polypow_gmpy2, dice_squaring, dice_squaring_gmpy2,
        dice, dice_gmpy2, dice_numpy, dice_gen]

# small cases to test correctness
for f in funs:
    print f.__doc__
    print f(6, 4)
    print f(7, 5)
    print


def test(fun, faces, num):
    """ Print best time out of many runs. """
    print f.__doc__
    t = timeit.timeit("%s(%s, %s)" % (f.__name__, faces, num),
                      setup="from __main__ import %s" % (f.__name__), number=1)
    # run up to 15 min and up to 100 times
    r = min(int(900.0/t), 10)
    print "Rounds: ", r
    print min(timeit.repeat("%s(%s, %s)" % (f.__name__, faces, num),
                            setup="from __main__ import %s" % (f.__name__),
                            number=1, repeat=r))

# fast methods
for f in funs[6:7]:
    test(f, 100, 1000)
for f in funs[6:7]:
    test(f, 100, 2000)
exit(0)

# very slow methods
for f in funs[2:4]:
    test(f, 100, 128)

# slow methods
for f in funs[:2]:
    test(f, 100, 500)
