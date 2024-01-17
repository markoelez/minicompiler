#!/bin/bash
rm test123
rm eval/out
#ld -o eval/out eval/out.o -platform_version macos 14.0 11.0 -arch arm64 -e _start
ld -o test123 test123.o -platform_version macos 14.0 11.0 -arch arm64 -e _start
