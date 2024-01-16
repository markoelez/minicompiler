#!/usr/bin/env python3
import os
import sys
from tokenizer import tokenize, Directive, Label, BinaryOp, UnaryOp
from macho import MachoObjectBuilder, Nlist64, N_TYPE, N_EXT


class Assembler:
    def __init__(self, tokens):
        # input
        self.tokens = tokens

        # output
        self.dat: bytes = bytes()

        # tables
        self.symbol_table = {}
        self.global_symbols = set()
        self.string_table = {}

        # misc. metadata
        self.lc = 0
        self.stidx = 1
        self.align = 4

        # dsymtab metadata
        self.ilocalsym: int = 0
        self.nlocalsym: int = 0
        self.iextdefsym: int = 0
        self.nextdefsym: int = 0
        self.iundefsym: int = 0

        # util
        self.is_immediate = lambda x: x[0] == '#'
        self.is_register = lambda x: x[0] == 'X'
        self.is_label = lambda x: x.isalpha() and not self.is_immediate(x) and not self.is_register(x)

        self.first_pass = True

    def _process_directive(self, token: Directive):
        match token.name:
            case '.global':
                self.global_symbols.add(token.subject)
            case '.align':
                self.align = int(token.subject)
                # TODO: update location counter to conform to specified boundary
            case '.ascii':
                s = token.subject.encode()
                self.lc += len(s)

    def _process_label(self, token: Label):
        if not self.first_pass: return
        self.symbol_table[token.name] = self.lc
        self.string_table[token.name] = self.stidx
        # string + separator
        self.stidx += len(token.name.encode()) + 1

    def _process_binary_op(self, token: BinaryOp):
        match token.name:
            case 'mov':
                self.lc += 4
            case 'adr':
                # second pass
                if token.s2 in self.symbol_table:
                    # TODO
                    pass
                self.lc += 4

    def _process_unary_op(self, token: UnaryOp):
        match token.name:
            case 'svc':
                self.lc += 4

    def process(self, token):
        match token:
            case Directive():
                return self._process_directive(token)
            case Label():
                return self._process_label(token)
            case BinaryOp():
                return self._process_binary_op(token)
            case UnaryOp():
                return self._process_unary_op(token)

    def _get_symbols(self) -> list[Nlist64]:
        res = []
        for symbol in self.symbol_table:

            x = Nlist64(
                n_strx=self.string_table[symbol],
                n_type=N_TYPE,
                n_sect=1,  # hardcode 1 section for now
                n_desc=0,
                n_value=self.symbol_table[symbol]
            )

            if symbol in self.global_symbols: x.n_type |= N_EXT

            res.append(x)

        return res

    def _get_string_table(self) -> list[str]:
        return list(self.string_table.keys())

    def dump(self, path: str) -> bytes:

        # first pass
        for x in self.tokens: self.process(x)
        self.first_pass = False

        # second pass
        for x in self.tokens: self.process(x)

        # create executable
        b = MachoObjectBuilder()
        b.add_header()
        # ****************** load commands ******************
        # single text section for now
        b.add_segment_lc(segname='__TEXT')
        b.add_section_lc(sectname='__text', segname='__TEXT', align=self.align)
        # build version is optional
        b.add_build_version_lc(platform=0x1, minos=0xe0000)
        b.add_symtab_lc()
        b.add_dysymtab_lc(
            ilocalsym=self.ilocalsym,
            nlocalsym=self.nlocalsym,
            iextdefsym=self.iextdefsym,
            nextdefsym=self.nextdefsym,
            iundefsym=self.iundefsym,
        )
        # ****************** data segments ******************
        b.add_code(dat=self.dat)
        b.add_symbol_table(symbols=self._get_symbols())
        b.add_string_table(table=self._get_string_table())
        o = b.build()

        # with open(path, 'wb') as fp: fp.write(o)


if __name__ == '__main__':

    assert len(sys.argv) > 1

    p = sys.argv[1]

    assert p.endswith('.s')
    assert os.path.isfile(p)

    with open(p, 'r') as fp:

        s = fp.read().strip()

        tokens = tokenize(s)

        for x in tokens: print(x)
        print()

        Assembler(tokens).dump('test123.o')
