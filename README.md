# minicompiler

[![CI](https://github.com/markoelez/minicompiler/actions/workflows/ci.yaml/badge.svg)](https://github.com/markoelez/minicompiler/actions/workflows/ci.yaml)


### Example

Running: `PYTHONPATH=. python minicompiler/eval.py`

Produces the following visual output:

```sh
********************************************************************************
int _start() {
        int x = 3;
        int y = 4;
        int res = x + y;
        return res;
    }
********************************************************************************
|-Root()
    |-FunctionDecl(rtype=T(type=<TokType.INT>, data='int'), ident=_start)
        |-CompoundStmt()
            |-DeclStmt()
                |-VarDecl(type='int', ident='x')
                    |-NumExpr(val=3)
            |-DeclStmt()
                |-VarDecl(type='int', ident='y')
                    |-NumExpr(val=4)
            |-DeclStmt()
                |-VarDecl(type='int', ident='res')
                    |-AddOp()
                        |-DeclRefExpr(ident='x')
                        |-DeclRefExpr(ident='y')
            |-ReturnStmt()
                |-DeclRefExpr(ident='res')
********************************************************************************
.global _start
_start:
MOV X16, #3
MOV X18, X16
MOV X26, #4
MOV X15, X26
ADD X7, X18, X15
MOV X12, X7
MOV X0, X12
RET
********************************************************************************
Directive(name='.global', subject='_start')
Label(name='_start')
MOV(X16, #3)         0x70 0x00 0x80 0xD2   01110000 00000000 10000000 11010010
MOV(X18, X16)        0xF2 0x03 0x10 0xAA   11110010 00000011 00010000 10101010
MOV(X26, #4)         0x9A 0x00 0x80 0xD2   10011010 00000000 10000000 11010010
MOV(X15, X26)        0xEF 0x03 0x1A 0xAA   11101111 00000011 00011010 10101010
ADD(X7, X18, X15)    0x47 0x02 0x0F 0x8B   01000111 00000010 00001111 10001011
MOV(X12, X7)         0xEC 0x03 0x07 0xAA   11101100 00000011 00000111 10101010
MOV(X0, X12)         0xE0 0x03 0x0C 0xAA   11100000 00000011 00001100 10101010
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
