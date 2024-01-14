#!/usr/bin/env python3

import struct
from dataclasses import dataclass, field
from pprint import pprint
from enum import Enum
from collections import defaultdict


# Constants.
LC_SEGMENT_64 = 0x00000019              # LC_SEGMENT_64 command type
LC_BUILD_VERSION = 0x32
MH_MAGIC_64 = 0xfeedfacf                # Mach-O 64-bit magic number
CPU_TYPE_ARM64 = 0x0100000c             # CPU type ARM64
CPU_SUBTYPE_ARM64_ALL = 0x00000000      # ARM64 subtype for all ARM64 CPUs
MH_OBJECT = 0x1                         # File type: object file
MH_FLAGS = 0                            # No flags set
MH_SUBSECTIONS_VIA_SYMBOLS = 0x2000
VM_PROT_READ = 0x01
VM_PROT_EXECUTE = 0x04
S_REGULAR = 0x0
S_ATTR_PURE_INSTRUCTIONS = 0x80000000
S_ATTR_SOME_INSTRUCTIONS = 0x40000000
LC_SYMTAB = 0x2
N_TYPE = 0x0e
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


class Component:
    def pack(self):
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
class Header(Component):
    magic: DTYPE.uint32_t = 0
    cputype: DTYPE.uint32_t = 0
    cpusubtype: DTYPE.uint32_t = 0
    filetype: DTYPE.uint32_t = 0
    ncmds: DTYPE.uint32_t = 0
    sizeofcmds: DTYPE.uint32_t = 0
    flags: DTYPE.uint32_t = 0
    reserved: DTYPE.uint32_t = 0


@dataclass(repr=False)
class Segment(Component):
    cmd: DTYPE.uint32_t = LC_SEGMENT_64
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
class Section(Component):
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
class SymtabCmd(Component):
    cmd: DTYPE.uint32_t = LC_SYMTAB
    cmdsize: DTYPE.uint32_t = 0
    symoff: DTYPE.uint32_t = 0
    nsyms: DTYPE.uint32_t = 0
    stroff: DTYPE.uint32_t = 0
    strsize: DTYPE.uint32_t = 0


@dataclass(repr=False)
class BuildCmd(Component):
    cmd: DTYPE.uint32_t = LC_BUILD_VERSION
    cmdsize: DTYPE.uint32_t = 0
    platform: DTYPE.uint32_t = 0
    minos: DTYPE.uint32_t = 0
    sdk: DTYPE.uint32_t = 0
    ntools: DTYPE.uint32_t = 0


@dataclass(repr=False)
class DysymtabCmd(Component):
    cmd: DTYPE.uint32_t = LC_DYSYMTAB
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
class Nlist64(Component):
    n_strx: DTYPE.uint32_t = 0
    n_type: DTYPE.uint8_t = 0
    n_sect: DTYPE.uint8_t = 0
    n_desc: DTYPE.uint16_t = 0
    n_value: DTYPE.uint64_t = 0


@dataclass(repr=False)
class GenericDataSegment(Component):
    dat: bytes = bytes()

    def pack(self):
        return self.dat

    def bsize(self) -> int:
        return len(self.dat)


@dataclass(repr=False)
class StringTableSegment(Component):
    table: list[str] = field(default_factory=list)

    def pack(self):
        t = '\0'.join(self.table)
        if t: t = '\0' + t
        return t.encode()

    def bsize(self) -> int:
        return len(self.pack())


@dataclass(repr=False)
class RelocInfo(Component):
    r_address: DTYPE.uint32_t = 0
    r_info: DTYPE.uint32_t = 0


def build_reloc_info(r_address: int, r_symbolnum: int, r_pcrel: int, r_length: int, r_extern: int, r_type: int) -> RelocInfo:
    r_info = (r_symbolnum & 0xFFFFFF) | (r_pcrel << 24) | (r_length << 25) | (r_extern << 27) | (r_type << 28)
    return RelocInfo(r_address, r_info)


class MachoObjectBuilder:
    def __init__(self):
        self.header: Header | None = None
        self.load_commands: list[Component] = []
        self.segments_by_segname: dict[str, Segment] = {}
        self.sections_by_segname: defaultdict[str, list[Section]] = defaultdict(list)

        # data
        self.data_segments: list[Component] = []
        self.symbols: list[Nlist64] = []
        self.str_table: bytes = bytes()
        self.code: bytes = bytes()

    def add_header(self, flags: int = 0):
        assert self.header is None

        self.header = Header(
            magic=MH_MAGIC_64,
            cputype=CPU_TYPE_ARM64,
            cpusubtype=CPU_SUBTYPE_ARM64_ALL,
            filetype=MH_OBJECT,
            ncmds=0,
            sizeofcmds=0,
            flags=flags
        )

    def add_segment_lc(self, segname: str = '', **kwargs):
        lc = Segment(
            segname=segname,
            maxprot=VM_PROT_READ | VM_PROT_EXECUTE,
            initprot=VM_PROT_READ | VM_PROT_EXECUTE,
            **kwargs
        )
        self.segments_by_segname[segname] = lc
        self.load_commands.append(lc)

    def add_section_lc(self, sectname: str = '', segname: str = '', align: int = 2, **kwargs):
        assert segname in self.segments_by_segname
        flags = S_REGULAR | S_ATTR_PURE_INSTRUCTIONS | S_ATTR_SOME_INSTRUCTIONS
        lc = Section(
            sectname=sectname,
            segname=segname,
            align=align,
            flags=flags,
            **kwargs
        )
        self.sections_by_segname[segname].append(lc)

    def add_build_version_lc(self, **kwargs):
        lc = BuildCmd(**kwargs)
        self.load_commands.append(lc)

    def add_symtab_lc(self, **kwargs):
        lc = SymtabCmd(**kwargs)
        self.load_commands.append(lc)

    def add_dysymtab_lc(self, **kwargs):
        lc = DysymtabCmd(**kwargs)
        self.load_commands.append(lc)

    def add_code(self, dat: bytes):
        ds = GenericDataSegment(dat=dat)
        self.code = dat
        self.data_segments.append(ds)

    def add_symbol_table(self, symbols: list[Nlist64] = []):
        self.symbols.extend(symbols)
        self.data_segments.extend(symbols)

    def add_string_table(self, table: list[str]):
        ds = StringTableSegment(table)
        self.str_table = ds.pack()
        self.data_segments.append(ds)

    def build(self) -> bytes:

        res = bytes()
        components = []

        # **************************** write header ****************************
        assert self.header is not None
        self.header.ncmds = len(self.load_commands)
        self.header.sizeofcmds = 0
        self.header.sizeofcmds += sum(x.bsize() for x in self.load_commands)
        # Add associated sections.
        self.header.sizeofcmds += sum([s.bsize() for lc in self.load_commands if hasattr(lc, 'segname') for s in self.sections_by_segname[lc.segname]])
        res += self.header.pack()

        # **************************** write load commands ****************************
        for lc in self.load_commands:
            match lc:
                case Segment():
                    assert lc.segname in self.sections_by_segname
                    secs = self.sections_by_segname[lc.segname]
                    lc.cmdsize = lc.bsize() + sum(x.bsize() for x in secs)
                    lc.filesize = len(self.code)  # TODO: make this better
                    lc.vmsize = lc.filesize
                    lc.fileoff = self.header.sizeofcmds + self.header.bsize()
                    lc.nsects = 1
                    components.append(lc)

                    # Sections associated with segment.
                    offset = self.header.sizeofcmds + self.header.bsize()
                    for sec in secs:
                        sec.size = len(self.code)  # TODO: make this better
                        sec.offset = offset
                        sec.reloff = offset + lc.filesize
                        sec.nreloc = 0  # TODO
                        offset += sec.size
                        components.append(sec)
                        self.header.sizeofcmds += sec.bsize()

                case BuildCmd():
                    lc.cmdsize = lc.bsize()
                    components.append(lc)

                case SymtabCmd():
                    lc.cmdsize = lc.bsize()
                    lc.symoff = offset
                    lc.nsyms = len(self.symbols)
                    lc.stroff = lc.symoff + sum(x.bsize() for x in self.symbols)
                    lc.strsize = len(self.str_table)
                    components.append(lc)

                case DysymtabCmd():
                    lc.cmdsize = lc.bsize()
                    components.append(lc)

        for lc in components: res += lc.pack()

        # **************************** write data ****************************
        for ds in self.data_segments:
            res += ds.pack()

        return res


if __name__ == '__main__':

    b = MachoObjectBuilder()
    b.add_header()
    # load commands
    b.add_segment_lc(segname='__TEXT')
    b.add_section_lc(sectname='__text', segname='__TEXT')
    b.add_build_version_lc(platform=0x1, minos=0xe0000)
    b.add_symtab_lc()
    b.add_dysymtab_lc(
        ilocalsym=0,
        nlocalsym=2,
        iextdefsym=2,
        nextdefsym=0,
        iundefsym=2,
    )
    # data segments
    b.add_code(dat=bytes([
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
    ]))
    b.add_symbol_table(symbols=[
        Nlist64(
            n_strx=1,
            n_type=N_TYPE | N_EXT,
            n_sect=1,
            n_desc=0,
            n_value=0
        ),
        Nlist64(
            n_strx=8,
            n_type=N_TYPE,
            n_sect=1,
            n_desc=0,
            n_value=0
        ),
    ])
    b.add_string_table(table=['_start', 'helloworld'])
    o = b.build()

    with open('out.o', 'wb') as fp: fp.write(o)
