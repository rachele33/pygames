BINS=draw.so
OBJS=draw.o
INCS=draw.hpp

CXXFLAGS=-fPIC -O2 -march=native

all: $(BINS)

$(OBJS): $(INCS)

draw.so: $(OBJS)
	$(CXX) $(CXXFLAGS) -shared -o $@ $^

test: all
	./bricks.py

clean:
	rm -f $(OBJS) $(BINS)

