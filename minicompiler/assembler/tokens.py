import struct
from dataclasses import dataclass, field
from abc import abstractmethod


@dataclass
class Token:
    name: str


@dataclass
class Label(Token):
    pass


@dataclass
class Directive(Token):
    subject: str


@dataclass
class Instruction(Token):
    name: str = field(repr=False)

    @abstractmethod
    def decode(self, b: bool = True) -> int | bytes:
        raise NotImplementedError()

    def __repr__(self):
        r = _fmt_int(self.decode(b=False))
        b = _fmt_bytes(self.decode(b=True))
        n = self.__class__.__name__
        e = {'name'}
        a = '(' + ', '.join(f'{v}' for k, v in self.__dict__.items() if k not in e) + ')'
        return f'{n}{a:<15}   {b}   {r}'

# ***************************** binary ops *****************************


opcodes = {
    'movz': 0b100101,
    'mov': 0b0101010,
    'adr': 0b10000,
    'add': 0b10001011000,
}

registers = {
    'X0': 0b00000,
    'X1': 0b00001,
    'X2': 0b00010,
    'X3': 0b00011,
    'X4': 0b00100,
    'X5': 0b00101,
    'X6': 0b00110,
    'X7': 0b00111,
    'X8': 0b01000,
    'X9': 0b01001,
    'X10': 0b01010,
    'X11': 0b01011,
    'X12': 0b01100,
    'X13': 0b01101,
    'X14': 0b01110,
    'X15': 0b01111,
    'X16': 0b10000,
    'X17': 0b10001,
    'X18': 0b10010,
    'X19': 0b10011,
    'X20': 0b10100,
    'X21': 0b10101,
    'X22': 0b10110,
    'X23': 0b10111,
    'X24': 0b11000,
    'X25': 0b11001,
    'X26': 0b11010,
    'X27': 0b11011,
    'X28': 0b11100,
    'X29': 0b11101,
    'X30': 0b11110
}


@dataclass(repr=False)
class MOV(Instruction):
    s1: str
    s2: str

    # ISA page 1795, 1801
    def decode(self, b: bool = True) -> int | bytes:
        # immediate -> register
        if self.s2[0] == '#':
            out = 0
            out |= 1 << 31                 # [31] sf -- 64-bit variant
            out |= 0b10 << 29              # [29-30] movz identifier
            out |= opcodes['movz'] << 23   # [23-28] opcode
            out |= int(self.s2[1:]) << 5   # [5-20] immediate value
            out |= registers[self.s1]      # [0-4] destination register
            if not b: return out
            return struct.pack('<I', out)
        # register -> register
        if self.s2[0] == 'X':
            out = 0
            out |= 0b101010100 << 23          # [24-31] opcode
            out |= registers[self.s2] << 16  # [16-20] source register
            out |= 0b11111 << 5              # [5-9] zero register (XZR)
            out |= registers[self.s1]        # [0-4] destination register
            if not b: return out
            return struct.pack('<I', out)
        raise ValueError()


@dataclass(repr=False)
class ADR(Instruction):
    s1: str
    s2: str
    imm: int = 0

    # ISA page 1269
    def decode(self, b: bool = True) -> int | bytes:
        # TODO: differentiate between MOV variants
        out = 0
        out |= (self.imm & 0x3) << 29            # [29-30] 2-bit lower immediate
        out |= opcodes['adr'] << 24              # [24-28] opcode
        out |= ((self.imm >> 2) & 0x7FFFF) << 5  # [5-23] 19-bit upper immediate
        out |= registers[self.s1]                # [0-4] destination register
        if not b: return out
        return struct.pack('<I', out)


def _fmt_bytes(b: bytes) -> str:
    return " ".join(f"0x{x:02X}" for x in b)


def _fmt_int(x: int) -> str:
    return " ".join([format(x, '032b')[i:i + 8] for i in range(0, len(format(x, '032b')), 8)][::-1])


@dataclass(repr=False)
class ADD(Instruction):
    dst: str
    s1: str
    s2: str

    # ISA page 1254
    def decode(self, b: bool = True) -> int | bytes:
        out = 0
        out |= opcodes['add'] << 21      # [21-31] opcode
        out |= registers[self.s2] << 16  # [16-20] src register 2
        out |= registers[self.s1] << 5   # [5-9] src register 1
        out |= registers[self.dst]       # [0-4] destination register
        if not b: return out
        return struct.pack('<I', out)

# ***************************** unary ops *****************************


@dataclass(repr=False)
class SVC(Instruction):
    s1: str

    # ISA page 1269
    def decode(self, b: bool = True) -> int | bytes:

        imm = int(self.s1[1:], 16)

        out = 0
        out |= 0b11010100000 << 21
        out |= (imm & 0x7FFF) << 5
        out |= 0b00001
        if not b: return out
        return struct.pack('<I', out)


@dataclass(repr=False)
class RET(Instruction):

    # ISA page 1850
    def decode(self, b: bool = True) -> int | bytes:
        out = 0
        out |= 0b11010110 << 24       # [23-31] static
        out |= 0b10 << 21             # [21-22] opcode
        out |= 0b11111 << 16          # [16-20] 1s
        out |= registers['X30'] << 5  # [5-9] destination register
        if not b: return out
        return struct.pack('<I', out)
