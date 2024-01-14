#!/bin/bash
ld -o out out.o -platform_version macos 14.0 11.0 -arch arm64 -e _start
