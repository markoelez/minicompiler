#!/bin/bash

rm eval/*.o eval/out

clear

./macho.py

otool -h eval/out.o

echo "****************************************************************************"

otool -l eval/out.o

echo "****************************************************************************"

./link.sh

./eval/out
