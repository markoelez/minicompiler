#!/bin/bash

rm out
rm out.o

clear && PYTHONPATH=. python assembler/main.py assembler/eval/test.s out.o

ld -o out out.o -platform_version macos 14.0 11.0 -arch arm64 -e _start

echo "*******************************************************************"

./out
