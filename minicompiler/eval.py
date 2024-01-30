#!/usr/bin/env python3
import subprocess
import random
from minicompiler.compiler.main import compile  # pylint: disable=redefined-builtin
from minicompiler.assembler.tokenizer import tokenize
from minicompiler.assembler.main import Assembler

random.seed(1331)


def run_asserting_success(cmd: list[str], rcode: int = 0):
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert res.returncode == rcode, f'ERROR! {res.stderr}'
    return res.stdout


if __name__ == '__main__':

    # static metadata
    obj_file = 'tmp.o'
    bin_file = 'out'

    print('*' * 80)

    # raw C program
    s = '''
    int _start() {
        int x = 3;
        int y = 4;
        int res = x + y;
        return res;
    }
    '''.strip()
    print(s)
    print('*' * 80)

    # C program -> ARM assembly IR (compilation)
    asm = compile(s, verbose=True)
    print(asm)
    print('*' * 80)

    # TODO: condense tokenization + parsing (two steps below)
    # ASM assembly -> ASM tokens
    tokens = tokenize(asm)
    for x in tokens: print(x)
    print('*' * 80)

    # ASM tokens -> binary
    Assembler(tokens).dump(obj_file)

    # Assertions.
    cmd = ["ld", "-o", bin_file, obj_file, "-platform_version", "macos", "14.0", "11.0", "-arch", "arm64", "-e", "_start"]
    run_asserting_success(cmd, 0)

    cmd = [f"./{bin_file}"]
    run_asserting_success(cmd, 7)
