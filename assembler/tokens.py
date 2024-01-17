import struct
from dataclasses import dataclass
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

    @abstractmethod
    def decode(self) -> bytes:
        raise NotImplementedError()

# ***************************** binary ops *****************************


opcodes = {
    'movz': 0b100101,
    'adr': 0b10000,
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
    'X16': 0b10000
}


@dataclass
class MOV(Instruction):
    s1: str
    s2: str

    # ISA page 1801
    def decode(self) -> bytes:
        # TODO: differentiate between MOV variants
        out = 0
        out |= 1 << 31                 # sf -- 64-bit variant
        out |= 0b10 << 29              # movz identifier
        out |= opcodes['movz'] << 23   # opcode
        out |= int(self.s2[1:]) << 5   # immediate value
        out |= registers[self.s1]      # destination register
        return struct.pack('<I', out)


@dataclass
class ADR(Instruction):
    s1: str
    s2: str
    imm: int = 0

    # ISA page 1269
    def decode(self) -> bytes:
        # TODO: differentiate between MOV variants
        out = 0
        out |= (self.imm & 0x3) << 29            # [29-30] 2-bit lower immediate
        out |= opcodes['adr'] << 24              # [24-28] opcode
        out |= ((self.imm >> 2) & 0x7FFFF) << 5  # [5-23] 19-bit upper immediate
        out |= registers[self.s1]                # [0-4] destination register
        return struct.pack('<I', out)

# ***************************** unary ops *****************************


@dataclass
class SVC(Instruction):
    s1: str

    # ISA page 1269
    def decode(self) -> bytes:

        imm = int(self.s1[1:], 16)

        out = 0
        out |= 0b11010100000 << 21
        out |= (imm & 0x7FFF) << 5
        out |= 0b00001
        return struct.pack('<I', out)
