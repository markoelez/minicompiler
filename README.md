# minicompiler

[![CI](https://github.com/markoelez/minicompiler/actions/workflows/ci.yaml/badge.svg)](https://github.com/markoelez/minicompiler/actions/workflows/ci.yaml)


### Example

Running: `PYTHONPATH=. python minicompiler/eval.py`

Produces the following visual output:

```sh
********************************************************************************
int _start() {
        int x = 3;
        int result = x + 42;
        return result;
    }
********************************************************************************
|-Root()
    |-FunctionDecl(rtype=T(type=<TokType.INT>, data='int'), ident=_start)
        |-CompoundStmt()
            |-DeclStmt()
                |-VarDecl(type='int', ident='x')
                    |-NumExpr(val=3)
            |-DeclStmt()
                |-VarDecl(type='int', ident='result')
                    |-AddOp()
                        |-DeclRefExpr(ident='x')
                        |-NumExpr(val=42)
            |-ReturnStmt()
                |-DeclRefExpr(ident='result')
********************************************************************************
.global _start
_start:
MOV X16, #3
MOV X18, X16
MOV X26, #42
ADD X12, X18, X26
MOV X15, X12
MOV X0, X15
RET
********************************************************************************
Directive(name='.global', subject='_start')
Label(name='_start')
MOV(X16, #3)         0x70 0x00 0x80 0xD2   01110000 00000000 10000000 11010010
MOV(X18, X16)        0xF2 0x03 0x10 0xAA   11110010 00000011 00010000 10101010
MOV(X26, #42)        0x5A 0x05 0x80 0xD2   01011010 00000101 10000000 11010010
ADD(X12, X18, X26)   0x4C 0x02 0x1A 0x8B   01001100 00000010 00011010 10001011
MOV(X15, X12)        0xEF 0x03 0x0C 0xAA   11101111 00000011 00001100 10101010
MOV(X0, X15)         0xE0 0x03 0x0F 0xAA   11100000 00000011 00001111 10101010
RET()                0xC0 0x03 0x5F 0xD6   11000000 00000011 01011111 11010110
********************************************************************************
```

In addition to an object file `tmp.o`, and an executable Mach-O binary `out`.

The raw C program goes through the following distinct transformations:

(compiler)
- C program -> C language tokens
- C language tokens -> AST
- AST -> ARM64 assembly

(assembler)
- ARM64 assembly -> ARM64 tokens
- ARM64 tokens -> Mach-O object file

(linker -- uses GNU linker)
- Mach-O object file -> Mach-O executable file

### Reference

ARM:
- https://developer.arm.com/documentation/102374/latest/
- http://163.238.35.161/~zhangs/arm64simulator/

Compilation:
- https://clang.llvm.org/docs/IntroductionToTheClangAST.html

Mach-O: 
- https://alexdremov.me/mystery-of-mach-o-object-file-builders/
- https://github.com/alexdremov/MachOBuilder/tree/main
- https://github.com/aidansteele/osx-abi-macho-file-format-reference?ref=alexdremov.me
- https://en.wikipedia.org/wiki/Mach-O#Mach-O_file_layout
- https://medium.com/@travmath/understanding-the-mach-o-file-format-66cf0354e3f4

### Todo
- better support for functions
    - support multiple functions + populate symbol/string tables
    - support stack frames
    - support calling functions with arguments
- put raw data into data section in object file
- support more instructions
    - conditionals
    - other binops (MUL, SUB, ...)
    - pointers, malloc, etc.
- support stdlib
