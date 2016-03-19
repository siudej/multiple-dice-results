CFLAGS = -O3 -I/usr/local/include -L/usr/local/lib
LIBS = -lgmp -lgmpxx
CPP5 = $(shell which g++-5 || which g++)

all: dice.out diceomp.out

dice.out: dice.cpp
	g++ $(CFLAGS) -o dice.out dice.cpp $(LIBS)

diceomp.out: diceomp.cpp
	$(CPP5) $(CFLAGS) -fopenmp -o diceomp.out diceomp.cpp $(LIBS)

clean:
	$(RM) dice.out 
	$(RM) diceomp.out 
