import darmtbl
import sys
import textwrap


def instruction_name(x):
    return x.split('{')[0].split('<')[0].split()[0]


def instruction_names(arr):
    """List of all unique instruction names."""
    return sorted(set(instruction_name(x[0]) for x in arr))


def instruction_names_enum(arr):
    """Enumeration of all instruction names."""
    text = ', '.join('I_%s' % x for x in instruction_names(arr))
    text = '\n    '.join(textwrap.wrap(text, 74))
    return 'typedef enum {\n    %s\n} armv7_instr_t;\n' % text


def instruction_names_table(arr):
    """Table of strings of all instructions."""
    text = ', '.join('"%s"' % x for x in instruction_names(arr))
    text = '\n    '.join(textwrap.wrap(text, 74))
    return 'const char *armv7_mnemonics[] = {\n    %s\n};' % text


def updates_condition_flags(arr):
    """List of all instructions that have the S flag."""
    return sorted(set(instruction_name(x[0]) for x in arr if darmtbl.S in x))


def updates_condition_flags_table(arr):
    """Lookup table returning True for instructions that have the S flag."""
    names = instruction_names(arr)
    flags = updates_condition_flags(arr)
    table = ', '.join(('1' if x in flags else '0') for x in names)
    text = '\n    '.join(textwrap.wrap(table, 74))
    return 'uint8_t updates_condition_flags[] = {\n    %s\n};' % text


def instruction_types_table(arr):
    """Lookup table for the types of instructions."""
    table = ', '.join(str(arr[x][0]) if x in arr else '-1'
                      for x in xrange(256))
    text = '\n    '.join(textwrap.wrap(table, 74))
    return 'uint8_t armv7_instr_types[] = {\n    %s\n};\n' % text


def instruction_names_index_table(arr):
    """Lookup table for instruction label for each instruction index."""
    table = ', '.join('I_%s' % str(arr[x][1]) if x in arr else '-1'
                      for x in xrange(256))
    text = '\n    '.join(textwrap.wrap(table, 74))
    return 'uint8_t armv7_instr_labels[] = {\n    %s\n};\n' % text

d = darmtbl

# we specify various instruction types
instr_types = [
    lambda x: x[0] == d.cond and d.Rn in x and d.Rd in x and x[-3] == d.type_ and x[-1] == d.Rm,
]

if __name__ == '__main__':
    uncond_table = {}
    cond_table = {}
    for description in darmtbl.ARMv7:
        instr = description[0]
        bits = description[1:]

        identifier = []
        remainder = []
        for x in xrange(1 if bits[0] == darmtbl.cond else 4, len(bits)-1):
            if isinstance(bits[x], int):
                identifier.append(bits[x])
            else:
                remainder = bits[x:]
                break

        for x in xrange(2**max(8-len(identifier), 0)):
            idx = sum(identifier[y]*2**(7-y) for y in xrange(len(identifier)))
            idx = int(idx + x)

            # for each instruction, check which type of instruction this is
            for instr_idx, y in enumerate(instr_types):
                if y(bits):
                    cond_table[idx] = instr_idx, instruction_name(instr)

    # python magic!
    sys.stdout = open(sys.argv[1], 'w')

    if sys.argv[1][-2:] == '.h':

        # print required headers
        print '#ifndef __ARMV7_TBL__'
        print '#define __ARMV7_TBL__'
        print '#include <stdint.h>'
        print

        # print some required definitions
        print 'uint8_t armv7_instr_types[256];'
        print 'uint8_t armv7_instr_labels[256];'
        print

        # print all instruction labels
        print instruction_names_enum(d.ARMv7)
        print '#endif'
        print

    elif sys.argv[1][-2:] == '.c':

        # print a header
        print '#include <stdio.h>'
        print '#include <stdint.h>'
        print '#include "%s"' % (sys.argv[1][:-2] + '.h')
        print

        # print a table containing all the types of instructions
        print instruction_types_table(cond_table)

        # print a table containing the instruction label for each entry
        print instruction_names_index_table(cond_table)