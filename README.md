# multiple-dice-results

How to optimize computations required to find the probability distribution of rolling a large number of dice?

This started when I read the following post from http://www.tizona-sci.com/2011/07/case-study-fast-scripts-for.html

The problem is not hard, but it involves arbitrarily large integers, so arithmetic operations enter into complexity considerations. In particular, multiplication should probably be avoided in favor of additions and subtractions.

There is a rather slow one line solution using numpy polynomial power.

It seems better to keep convolving with a list of ones (even compared to binary power computation method). The convolution requires only one addition and one subtraction to find the next number, and only one half needs to be computed.

Just for fun, I have also developed a generator and/or deque based solutions (may need higher recursion limit). The overhead is not so big and the generator is actually faster when looking for not so large sums.

### Running times

Taking 100 sides and 1000 dice I get
- 15 seconds for the iterative version (function dice2).
- 25 seconds for the generator (function dice4). Though sum of 10000 needs only 6s
- 30 seconds for 200 dice and the numpy polynomial power function

### Notes

There is almost no speed benefit in keeping long integers inside numpy array (type=object), as these cannot be handled by c compiled code. However this gives the convenience of using all numpy functions on such array with Python handling object related operations.
