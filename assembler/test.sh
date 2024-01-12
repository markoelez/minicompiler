#!/bin/bash

rm out.o

clear

./assembler.py

otool -h out.o

echo "****************************************************************************"

otool -l out.o
