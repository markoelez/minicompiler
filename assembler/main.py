#!/usr/bin/env python3
import os
import sys
from assembler.tokenizer import tokenize
from assembler.tokens import Directive, Label, Instruction, MOV, ADR, SVC
from assembler.macho import MachoObjectBuilder, Nlist64, N_TYPE, N_EXT


class Assembler:
    def __init__(self, tokens):
        # input
        self.tokens = tokens

        # output
        self.dat: bytes = bytes()

        # tables
        self.symbol_table = {}
        self.loc_symbols = set()
        self.ext_symbols = set()
        self.string_table = {}

        # misc. metadata
        self.lc = 0
        self.stidx = 1
        self.align = 4

        # util
        self.is_immediate = lambda x: x[0] == '#'
        self.is_register = lambda x: x[0] == 'X'
        self.is_label = lambda x: x.isalpha() and not self.is_immediate(x) and not self.is_register(x)

        self.first_pass = True

    def _process_directive(self, token: Directive):
        match token.name:
            case '.global':
                self.loc_symbols.discard(token.subject)
                self.ext_symbols.add(token.subject)
            case '.align':
                self.align = int(token.subject)
                # TODO: update location counter to conform to specified boundary
            case '.ascii':
                s = token.subject.encode()
                self.lc += len(s)
                if self.first_pass: return
                p = ' '.join(f'0x{b:02X}' for b in s)
                print(f'{p:<{10}}')
                self.dat += s

    def _process_label(self, token: Label):
        if not self.first_pass: return
        self.symbol_table[token.name] = self.lc
        self.string_table[token.name] = self.stidx
        # string + separator
        self.stidx += len(token.name.encode()) + 1
        self.loc_symbols.add(token.name)

    # TODO
    def _process_instruction(self, token: Instruction):

        out = bytes()
        match token:
            case MOV():
                out = token.decode()
                self.lc += 4
            case ADR():

                # first pass
                if token.s2 not in self.symbol_table: return

                # calculate offset
                addr = self.symbol_table[token.s2]
                imm = addr - self.lc + 4
                token.imm = imm  # type: ignore

                out = token.decode()
                self.lc += 4
            case SVC():
                out = token.decode()
                self.lc += 4

        if not self.first_pass:
            p = ' '.join(f'0x{b:02X}' for b in out)
            print(f'{p:<{10}} ---- {token}')
            self.dat += out

    def process(self, token):
        match token:
            case Directive():
                return self._process_directive(token)
            case Label():
                return self._process_label(token)
            case Instruction():
                return self._process_instruction(token)

    def _get_symbols(self) -> list[Nlist64]:
        res = []

        # group local and external symbols together
        for symbol in list(self.loc_symbols) + list(self.ext_symbols):

            is_local = symbol in self.loc_symbols

            x = Nlist64(
                n_strx=self.string_table[symbol],
                n_type=N_TYPE,
                n_sect=1,  # hardcode 1 section for now
                n_desc=0,
                n_value=self.symbol_table[symbol]
            )

            if not is_local: x.n_type |= N_EXT

            res.append(x)

        return res

    def _get_string_table(self) -> list[str]:
        return list(self.string_table.keys())

    def dump(self, path: str):

        # first pass
        for x in self.tokens: self.process(x)
        self.first_pass = False
        self.lc = 0

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
            ilocalsym=0 if len(self.loc_symbols) > 0 else len(self.ext_symbols),
            nlocalsym=len(self.loc_symbols),
            iextdefsym=len(self.loc_symbols),
            nextdefsym=len(self.ext_symbols),
            iundefsym=len(self.loc_symbols) + len(self.ext_symbols),
        )
        # ****************** data segments ******************
        b.add_code(dat=self.dat)
        b.add_symbol_table(symbols=self._get_symbols())
        b.add_string_table(table=self._get_string_table())
        o = b.build()

        with open(path, 'wb') as fp: fp.write(o)


if __name__ == '__main__':

    assert len(sys.argv) == 3

    p, o = sys.argv[1], sys.argv[2]

    assert p.endswith('.s')
    assert os.path.isfile(p)

    with open(p, 'r') as fp:

        s = fp.read().strip()

        tokens = tokenize(s)

        Assembler(tokens).dump(o)
