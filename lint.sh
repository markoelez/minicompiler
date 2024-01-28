#!/bin/bash
python -m mypy assembler/
python -m pylint assembler/

python -m mypy compiler/
python -m pylint compiler/
