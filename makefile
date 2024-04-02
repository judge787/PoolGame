CC=clang
CFLAGS=-Wall -pedantic -std=c99 -fPIC

# Set the path to the Python headers and libraries
PYTHON_INCLUDE=/usr/include/python3.11/
PYTHON_LIB=/usr/lib/python3.11

# The default target
all: libphylib.so _phylib.so

# Compile the C library into position-independent code (PIC)
phylib.o: phylib.c phylib.h
	$(CC) $(CFLAGS) -c $< -o $@

# Create a shared library from an object file
libphylib.so: phylib.o
	$(CC) -shared $< -o $@ -lm

# Generate wrapper code with SWIG
phylib_wrap.c: phylib.i
	swig -python phylib.i

# Compile the wrapper code
phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -I$(PYTHON_INCLUDE) -c $< -o $@

# Link the wrapper object file to create the Python shared library
_phylib.so: phylib_wrap.o
	$(CC) $(CFLAGS) -shared $< -L. -L$(PYTHON_LIB) -lpython3.11 -lphylib -o $@

# Clean target
clean:
	rm -f *.o *.so phylib_wrap.c phylib.py phylib.db

# Set the library path for runtime
export LD_LIBRARY_PATH := $(shell pwd)
