CFLAGS = -O3 -lgmpxx -lgmp -I/usr/local/include -L/usr/local/lib

all: dice.out diceomp.out

dice.out: dice.cpp
	g++ $(CFLAGS) -o dice.out dice.cpp

diceomp.out: diceomp.cpp
	g++-5 $(CFLAGS) -fopenmp -o diceomp.out diceomp.cpp

clean:
	$(RM) dice.out 
	$(RM) diceomp.out 
