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
    'add': 0b10001011001,
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


@dataclass
class ADD(Instruction):
    s1: str
    s2: str
    dst: str

    # ISA page 1254
    def decode(self) -> bytes:
        out = 0
        out |= opcodes['add'] << 21      # [21-31] opcode
        out |= registers[self.s2] << 16  # [16-20] src register 2
        out |= registers[self.s1] << 5   # [5-9] src register 1
        out |= registers[self.dst]       # [0-4] destination register
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


@dataclass
class RET(Instruction):
    def decode(self) -> bytes:
        return bytes()
