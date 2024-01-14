
import struct
from abc import abstractmethod
from dataclasses import dataclass
from pprint import pprint, pformat
from enum import Enum


# Constants.
LC_SEGMENT_64 = 0x00000019              # LC_SEGMENT_64 command type
LC_BUILD_VERSION = 0x32
MH_MAGIC_64 = 0xfeedfacf                # Mach-O 64-bit magic number
CPU_TYPE_ARM64 = 0x0100000c             # CPU type ARM64
CPU_SUBTYPE_ARM64_ALL = 0x00000000      # ARM64 subtype for all ARM64 CPUs
MH_OBJECT = 0x1                         # File type: Object file
MH_FLAGS = 0                            # No flags set
MH_SUBSECTIONS_VIA_SYMBOLS = 0x2000
VM_PROT_READ = 0x01
VM_PROT_EXECUTE = 0x04
S_REGULAR = 0x0
S_ATTR_PURE_INSTRUCTIONS = 0x80000000
S_ATTR_SOME_INSTRUCTIONS = 0x40000000
LC_SYMTAB = 0x2
N_SECT = 0x0e
N_EXT = 0x01
N_UNDF = 0x0
NO_SECT = 0
REFERENCE_FLAG_DEFINED = 0x000F
REFERENCE_FLAG_UNDEFINED_NON_LAZY = 0x000E
LC_DYSYMTAB = 0xB
GENERIC_RELOC_SECTDIFF = 0x0005


class DTYPE(Enum):
    uint8_t = 'B'     # 1 bytes
    uint16_t = 'H'    # 2 bytes
    uint32_t = 'I'    # 4 bytes
    uint64_t = 'Q'    # 8 bytes
    char_16b = '16s'  # 16 bytes


class Obj:
    def pack(self):
        b = 'Nlist64' in self.__class__.__name__
        s, vals = '', []
        for k, v in self.__annotations__.items():
            s += v.value
            x = vars(self)[k]
            vals.append(x.encode('utf-8') if isinstance(x, str) else x)
        return struct.pack(s, *vals)

    def bsize(self) -> int:
        s = ''.join(x.value for x in self.__annotations__.values())
        return struct.calcsize(s)

    def __repr__(self):
        hex_attrs = {k: (f'0x{v:x}' if isinstance(v, int) else v) for k, v in vars(self).items()}
        attr_str = ', '.join(f'{k}={v}' for k, v in hex_attrs.items())
        return f'{self.__class__.__name__}({attr_str})'


def dbg(o):
    print('*' * 120)
    pprint(o)
    print('*' * 120)


@dataclass(repr=False)
class Header(Obj):
    magic: DTYPE.uint32_t = 0
    cputype: DTYPE.uint32_t = 0
    cpusubtype: DTYPE.uint32_t = 0
    filetype: DTYPE.uint32_t = 0
    ncmds: DTYPE.uint32_t = 0
    sizeofcmds: DTYPE.uint32_t = 0
    flags: DTYPE.uint32_t = 0
    reserved: DTYPE.uint32_t = 0


@dataclass(repr=False)
class Segment(Obj):
    cmd: DTYPE.uint32_t = 0
    cmdsize: DTYPE.uint32_t = 0
    segname: DTYPE.char_16b = ''
    vmaddr: DTYPE.uint64_t = 0
    vmsize: DTYPE.uint64_t = 0
    fileoff: DTYPE.uint64_t = 0
    filesize: DTYPE.uint64_t = 0
    maxprot: DTYPE.uint32_t = 0
    initprot: DTYPE.uint32_t = 0
    nsects: DTYPE.uint32_t = 0
    flags: DTYPE.uint32_t = 0


@dataclass(repr=False)
class Section(Obj):
    sectname: DTYPE.char_16b = ''
    segname: DTYPE.char_16b = ''
    addr: DTYPE.uint64_t = 0
    size: DTYPE.uint64_t = 0
    offset: DTYPE.uint32_t = 0
    align: DTYPE.uint32_t = 0
    reloff: DTYPE.uint32_t = 0
    nreloc: DTYPE.uint32_t = 0
    flags: DTYPE.uint32_t = 0
    reserved1: DTYPE.uint32_t = 0
    reserved2: DTYPE.uint32_t = 0
    reserved3: DTYPE.uint32_t = 0


@dataclass(repr=False)
class SymtabCmd(Obj):
    cmd: DTYPE.uint32_t = 0
    cmdsize: DTYPE.uint32_t = 0
    symoff: DTYPE.uint32_t = 0
    nsyms: DTYPE.uint32_t = 0
    stroff: DTYPE.uint32_t = 0
    strsize: DTYPE.uint32_t = 0


@dataclass(repr=False)
class BuildCmd(Obj):
    cmd: DTYPE.uint32_t = 0
    cmdsize: DTYPE.uint32_t = 0
    platform: DTYPE.uint32_t = 0
    minos: DTYPE.uint32_t = 0
    sdk: DTYPE.uint32_t = 0
    ntools: DTYPE.uint32_t = 0


@dataclass(repr=False)
class DysymtabCmd(Obj):
    cmd: DTYPE.uint32_t = 0
    cmdsize: DTYPE.uint32_t = 0
    ilocalsym: DTYPE.uint32_t = 0
    nlocalsym: DTYPE.uint32_t = 0
    iextdefsym: DTYPE.uint32_t = 0
    nextdefsym: DTYPE.uint32_t = 0
    iundefsym: DTYPE.uint32_t = 0
    nundefsym: DTYPE.uint32_t = 0
    tocoff: DTYPE.uint32_t = 0
    ntoc: DTYPE.uint32_t = 0
    modtaboff: DTYPE.uint32_t = 0
    nmodtab: DTYPE.uint32_t = 0
    extrefsymoff: DTYPE.uint32_t = 0
    nextrefsyms: DTYPE.uint32_t = 0
    indirectsymoff: DTYPE.uint32_t = 0
    nindirectsyms: DTYPE.uint32_t = 0
    extreloff: DTYPE.uint32_t = 0
    nextrel: DTYPE.uint32_t = 0
    locreloff: DTYPE.uint32_t = 0
    nlocrel: DTYPE.uint32_t = 0


@dataclass(repr=False)
class Nlist64(Obj):
    n_strx: DTYPE.uint32_t = 0
    n_type: DTYPE.uint8_t = 0
    n_sect: DTYPE.uint8_t = 0
    n_desc: DTYPE.uint16_t = 0
    n_value: DTYPE.uint64_t = 0


@dataclass(repr=False)
class RelocInfo(Obj):
    r_address: DTYPE.uint32_t = 0
    r_info: DTYPE.uint32_t = 0


def build_reloc_info(r_address: int, r_symbolnum: int, r_pcrel: int, r_length: int, r_extern: int, r_type: int) -> RelocInfo:
    r_info = (r_symbolnum & 0xFFFFFF) | (r_pcrel << 24) | (r_length << 25) | (r_extern << 27) | (r_type << 28)
    return RelocInfo(r_address, r_info)


def write_macho(p: str):

    # **************************** init ****************************

    h = Header(
        magic=MH_MAGIC_64,
        cputype=CPU_TYPE_ARM64,
        cpusubtype=CPU_SUBTYPE_ARM64_ALL,
        filetype=MH_OBJECT,
        ncmds=0,
        sizeofcmds=0,
        flags=0  # MH_SUBSECTIONS_VIA_SYMBOLS,
    )

    seg = Segment(
        cmd=LC_SEGMENT_64,
        cmdsize=0,
        segname='',  # __TEXT',
        vmaddr=0,
        vmsize=0,
        fileoff=0,
        filesize=0,
        maxprot=0x00000007,  # VM_PROT_READ | VM_PROT_EXECUTE,
        initprot=0x00000007,  # VM_PROT_READ | VM_PROT_EXECUTE,
        nsects=2,
    )

    sec = Section(
        sectname='__text',
        segname='__TEXT',
        addr=0,
        size=0,
        offset=0,
        align=2,
        reloff=0,
        nreloc=0,
        flags=0x80000400  # S_REGULAR | S_ATTR_PURE_INSTRUCTIONS | S_ATTR_SOME_INSTRUCTIONS
    )

    build_cmd = BuildCmd(
        cmd=LC_BUILD_VERSION,
        cmdsize=0,
        platform=0x1,
        minos=0xe0000,
        sdk=0,
        ntools=0
    )

    symtab_cmd = SymtabCmd(
        cmd=LC_SYMTAB,
        cmdsize=0,
        symoff=0,
        nsyms=0,
        stroff=0,
        strsize=0,
    )

    code = bytes([
        0x20, 0x00, 0x80, 0xd2,
        0xe1, 0x00, 0x00, 0x10,
        0xc2, 0x01, 0x80, 0xd2,
        0x90, 0x00, 0x80, 0xd2,
        0x01, 0x10, 0x00, 0xd4,
        0x00, 0x00, 0x80, 0xd2,
        0x30, 0x00, 0x80, 0xd2,
        0x01, 0x10, 0x00, 0xd4,
        0x48, 0x65, 0x6c, 0x6c,
        0x6f, 0x2c, 0x20, 0x57,
        0x6f, 0x72, 0x6c, 0x64,
        0x21, 0x0a, 0x00, 0x00
    ])

    str_table = bytes([
        0x00, 0x5f, 0x73, 0x74, 0x61, 0x72, 0x74, 0x00, 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x00, 0x6c, 0x74, 0x6d, 0x70, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])

    symbols = [
        Nlist64(
            n_strx=0x13,
            n_type=0x0e,
            n_sect=1,
            n_desc=0,
            n_value=0
        ),
        Nlist64(
            n_strx=8,
            n_type=0x0e,
            n_sect=1,
            n_desc=0,
            n_value=0
        ),
        Nlist64(
            n_strx=1,
            n_type=0x0f,
            n_sect=1,
            n_desc=0,
            n_value=0
        ),
    ]

    dysymtab_cmd = DysymtabCmd(
        cmd=LC_DYSYMTAB,
        cmdsize=0,
        ilocalsym=0,
        nlocalsym=2,
        iextdefsym=2,
        nextdefsym=1,
        iundefsym=3
    )

    reloc = [
        # build_reloc_info(1, 1, 1, 2, 1, GENERIC_RELOC_SECTDIFF),
        # build_reloc_info(6, 0, 1, 2, 1, GENERIC_RELOC_SECTDIFF)
    ]

    # **************************** write ****************************

    d = bytes()

    # Write header.
    h.ncmds = 4
    h.sizeofcmds = seg.bsize() + sec.bsize() + build_cmd.bsize() + symtab_cmd.bsize() + dysymtab_cmd.bsize()
    d += h.pack()

    # Write segment.
    seg.cmdsize = seg.bsize() + sec.bsize()
    seg.filesize = len(code)
    seg.vmsize = seg.filesize
    seg.fileoff = h.sizeofcmds + h.bsize()
    seg.nsects = 1
    d += seg.pack()

    # Write section.
    sec.size = seg.filesize
    sec.offset = seg.fileoff
    sec.reloff = seg.fileoff + seg.filesize
    sec.nreloc = len(reloc)
    d += sec.pack()

    # Write build command.
    build_cmd.cmdsize = build_cmd.bsize()
    d += build_cmd.pack()

    # Write symtab.
    symtab_cmd.cmdsize = symtab_cmd.bsize()
    symtab_cmd.symoff = h.sizeofcmds + sec.bsize() + sum(x.bsize() for x in reloc)
    symtab_cmd.nsyms = len(symbols)
    symtab_cmd.stroff = symtab_cmd.symoff + sum(x.bsize() for x in symbols)
    symtab_cmd.strsize = len(str_table)
    d += symtab_cmd.pack()

    # Write dysymtab.
    dysymtab_cmd.cmdsize = dysymtab_cmd.bsize()
    d += dysymtab_cmd.pack()

    # Write code.
    d += code

    # Write relocations.
    for x in reloc:
        d += x.pack()

    # Write symbol table.
    for x in symbols:
        d += x.pack()

    # Write string table.
    d += str_table

    with open(p, 'wb') as fp: fp.write(d)
