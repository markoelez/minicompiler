#!/bin/bash
#ld -o eval/out eval/out.o -platform_version macos 14.0 11.0 -arch arm64 -e _start
ld -o out test123.o -platform_version macos 14.0 11.0 -arch arm64 -e _start
