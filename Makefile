# Compiler
CC = clang

# Source file
SRC = eval/hello.c

# Executable name
EXE = hello

# Assembly output
ASM = hello.s

# Compiler flags
CFLAGS = -Wall -O2 -O0

# Default target
all: $(EXE) $(ASM)

# Compile the program
$(EXE): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(EXE)

# Generate assembly
$(ASM): $(SRC)
	$(CC) $(CFLAGS) -S $(SRC) -o $(ASM)

# Clean up build artifacts
clean:
	rm -f $(EXE) $(ASM)

.PHONY: all clean
