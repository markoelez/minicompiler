#!/bin/bash

rm -f tmp9.0
rm -f out

clear & PYTHONPATH=. python minicompiler/eval.py

#ld -o out tmp9.o -platform_version macos 14.0 11.0 -arch arm64 -e _start

#./out
