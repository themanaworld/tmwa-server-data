#!/usr/bin/env python

from __future__ import print_function

import hashlib
import sys


INTEGER_SIZE = 32

VAR_PREFIXES = [
        'script_var_persist:',
        'script_var_special:',
]

UNKNOWN = 'Quest Not Known'
KNOWN = 'Quest Available'
ACTIVE = 'Quest in Progress'
COMPLETE = 'Quest Complete'
# REPEAT = 'Quest Repeatable'
# STATUS = 'Quest Status'

# condition for printing other slices
OTHER_CONDITION = 'debug || getgmlevel()'
# condition for printing new (unknown) quests
NEW_CONDITION = 'debug || getgmlevel()'
# condition for printing bad states
ERROR_CONDITION = 'debug || getgmlevel()'


def get_vars(it):
    for line in it:
        for pfx in VAR_PREFIXES:
            if line.startswith(pfx):
                yield line[len(pfx):].strip()

def main(args=None):
    if args is None:
        args = sys.argv
    args = args[1:]
    if len(args) != 1:
        sys.exit('Usage: quest-log.py variables.conf > quest-log.txt')
    v = set()
    for a in args:
        with open(a) as f:
            v.update(get_vars(f))
    gen_script(v)

if 0:
    class States(object):
        __slots__ = ('name', 'shift', 'width', 'values', 'title')

        def __init__(self, name, shift, width, title):
            assert shift >= 0 and width > 0 and shift + width <= INTEGER_SIZE
            self.name = name
            self.shift = shift
            self.width = width
            self.title = title
            self.values = [None] * (1 << width)

        def __call__(self, value, desc, mode=ACTIVE):
            assert self.values[value] is None
            self.values[value] = ('%s: %s' % (mode, desc))
            return self

        def dump(self):
            print('    set @tmp, (%s >> %d) & ((1 << %d) - 1);' % (self.name, self.shift, self.width))
            print('    if (debug || @tmp)')
            print('        mes "##B%s##b";' % self.title)
            for i, desc in enumerate(self.values):
                if desc is None:
                    print('    if (debug && @tmp == %d)' % i)
                    print('        mes "debug: unknown state: " + @tmp;')
                    continue
                print('    if (@tmp == %d)' % i)
                print('        mes "%s";' % desc)

def gen_script(vars):
    vars = {name: [None] * INTEGER_SIZE for name in vars}

    for var in quest_vars:
        common = vars[var.slice.var_name]
        for i in range(var.slice.shift, var.slice.shift + var.slice.width):
            assert common[i] is None
            common[i] = var
    for var_name, common in vars.items():
        low_none = None
        for i in range(len(common)):
            if common[i] is not None:
                continue
            if low_none is None:
                low_none = i
            if i + 1 != len(common) and common[i] is None:
                continue
            ign = Undocumented(Slice(var_name, low_none, i + 1 - low_none))
            for j in range(low_none, i + 1):
                common[j] = ign

    print('// generated file, edit %s instead' % __file__)
    print('function|script|QuestLog')
    print('{')
    print('    callfunc "ClearVariables";')
    print('    goto L_Menu;')
    print()
    print('    // the beginning')
    print()
    print('L_Menu:')
    print('    menu')
    print('        "Known quests", L_Known,')
    print('        "Unknown quests (may require privileges)", L_Unknown,')
    print('        "Other slices (may require privileges)", L_Other,')
    print('        "All of the above", L_All;')
    print()
    print('L_Perm:')
    print('    mes "Permission denied";')
    print('    goto L_Menu;')
    print()
    print('L_Known:')
    print('    set @quest_known, 1;')
    print('    set @quest_unknown, 0;')
    print('    set @quest_error, (%s) != 0;' % ERROR_CONDITION)
    print('    set @quest_other, 0;')
    print('    goto L_First;')
    print()
    print('L_Unknown:')
    print('    if (!(%s))' % NEW_CONDITION)
    print('        goto L_Perm;')
    print('    set @quest_known, 0;')
    print('    set @quest_unknown, 1;')
    print('    set @quest_error, 0;')
    print('    set @quest_other, 0;')
    print('    goto L_First;')
    print()
    print('L_Doc:')
    print('    if (!(%s))' % OTHER_CONDITION)
    print('        goto L_Perm;')
    print('    set @quest_known, 0;')
    print('    set @quest_unknown, 0;')
    print('    set @quest_error, 0;')
    print('    set @quest_other, 1;')
    print('    goto L_First;')
    print()
    print('L_All:')
    print('    set @quest_known, 1;')
    print('    set @quest_unknown, (%s) != 0;' % NEW_CONDITION)
    print('    set @quest_error, (%s) != 0;' % ERROR_CONDITION)
    print('    set @quest_other, (%s) != 0;' % OTHER_CONDITION)
    print('    goto L_First;')
    print()
    print('L_First:')
    for name, var in sorted(vars.items()):
        print()
        print('    // %s' % name)
        print()
        prev = None
        xbegin = 0
        for p in var:
            if p is prev:
                continue
            prev = p
            assert xbegin == p.slice.shift
            p.dump()
            xbegin = p.slice.shift + p.slice.width
        assert xbegin == INTEGER_SIZE

        print('    if (%s)' % name)
        print('        next;')

    print()
    print('    // the end')
    print()
    print('    goto L_Close;')
    print()
    print('L_Close:')
    print('    set @quest_known, 0;')
    print('    set @quest_unknown, 0;')
    print('    set @quest_error, 0;')
    print('    set @quest_other, 0;')
    print('    close;')
    print('}')


def pretty_mask_size(width):
    assert width > 0
    rv = (width - 1) // 4
    i = 1
    # rv += 1; rv -= 1
    # round up to power of 2
    while rv & (rv + 1):
        rv |= rv >> i
        i <<= 1
    rv += 1
    return rv

class Slice(object):
    __slots__ = ('var_name', 'shift', 'width')

    def __init__(self, var, shift=None, width=None):
        if shift is None:
            assert width is None
            shift = 0
            width = INTEGER_SIZE
        elif width is None:
            width = 1
        assert shift >= 0 and width > 0 and shift + width <= INTEGER_SIZE
        self.var_name = var
        self.shift = shift
        self.width = width

    def expr(self):
        # python does the right thing with large shifts
        masksize = pretty_mask_size(self.width)
        mask = (1 << self.width) - 1
        return '((%s >> %d) & 0x%0*x)' % (self.var_name, self.shift, masksize, mask)

    def label(self):
        return '%s_%d_%d' % (self.var_name, self.shift, self.width)


    def ignored(self):
        return Ignored(self)

    def reserved(self, name):
        return Reserved(self, name)

    def counter(self, name):
        return Counter(self, name)

    def flag(self, name):
        assert self.width == 1, 'Flag must be a single bit'
        return Flag(self, name)

    def states(self, name):
        assert self.width > 1, 'Less than 2 states is a flag'
        assert self.width <= 8, 'More than 256 states is probably a bad idea'
        return States(self, name)

class SlicedData(object):
    __slots__ = ('slice', 'quest_name', 'conditions')

    def __init__(self, slice, name):
        self.slice = slice
        self.quest_name = name
        # no quest is in progress if its state is 0
        if isinstance(self, States):
            self.conditions = ['(@tmp || @quest_new)']
        else:
            self.conditions = ['@tmp']

    def condition(self, expr):
        self.conditions.append(expr)
        return self

    def label_after(self):
        label = self.slice.label()
        # unfortunately there is a limit
        if True:
            label = hashlib.md5(label).hexdigest()[:16]
        rv = 'L_Skip_%s' % label
        assert len(rv) <= 23, 'len(%s) = %d' % (rv, len(rv))
        return rv

    def dump(self):
        label = self.label_after()
        print('    set @tmp, %s;' % self.slice.expr())
        print('    if (!(%s))' % ' && '.join(self.conditions))
        print('        goto %s;' % label)
        self.impl_dump()
        print('    goto %s;' % label)
        print()
        print('%s:' % label)

    def dump_other(self, debug_name):
        var_name = self.slice.var_name
        shift = self.slice.shift
        width = self.slice.width
        field_name = '%s[%d:%d]' % (var_name, shift, shift + width)
        print('    if (@quest_other)')
        print('        mes "Debug: %s: %s = " + @tmp;' % (debug_name, field_name))

class Undocumented(SlicedData):
    __slots__ = ()

    def __init__(self, slice):
        SlicedData.__init__(self, slice, None)

    def impl_dump(self):
        self.dump_other('undocumented')

class Ignored(SlicedData):
    __slots__ = ()

    def __init__(self, slice):
        SlicedData.__init__(self, slice, None)

    def impl_dump(self):
        self.dump_other('ignored')


class Reserved(SlicedData):
    __slots__ = ()

    def impl_dump(self):
        self.dump_other('reserved')

class Counter(SlicedData):
    __slots__ = ()

    def impl_dump(self):
        print('    mes "##B%s##b: " + @tmp;' % self.quest_name)

class Flag(SlicedData):
    __slots__ = ()

    def impl_dump(self):
        print('    mes "##B%s##b: " + @tmp;' % self.quest_name)


class States(SlicedData):
    __slots__ = ('states')

    def __init__(self, slice, name):
        SlicedData.__init__(self, slice, name)
        self.states = [None] * (1 << slice.width)

    def __call__(self, num, desc, mode=ACTIVE):
        assert num != 0
        assert num == 1 or self.states[num - 1] is not None
        assert self.states[num] is None
        self.states[num] = '%s: %s' % (mode, desc)
        return self

    def impl_dump(self):
        last_state = None
        assert self.states[0] is None
        if self.states[0] is None:
            print('    if (@quest_new && @tmp == 0)')
            print('        mes "Debug: ##B%s##b: %s";' % (self.quest_name, UNKNOWN))
            print('    if (!@tmp || !@quest_known || !@quest_error)')
            print('        goto %s;' % self.label_after())
        for i, s in enumerate(self.states):
            if s is None:
                continue
            last_state = i
            print('    if (@quest_known && @tmp == %d)' % i)
            print('        mes "##B%s##b: %s";' % (self.quest_name, s))
        if last_state != len(self.states) - 1:
            print('    if (@quest_error && @tmp > %d)' % last_state)
            print('        mes "Debug: ##B%s##b: Invalid state: " + @tmp;' % self.quest_name)


quest_vars = [
# TODO split second half of quest
Slice('STARTAREA', 0, 4).states('Tutorial Quest / (TODO split) Attitude Adjustment')
(1, 'Walk over to the red carpet')
(2, 'Walk to the dresser and get some clothes to wear')
(3, 'Open your inventory and equip the clothes (###keyWindowEquipment;)')
(4, 'Go downstairs and find Tanisha')
(5, 'Tanisha wants help killing maggots')
(6, 'Kill the maggots with the knife or slingshot Tanisha gave you')
(7, 'You have defeated the maggots! Now talk to Tanisha')
(8, 'You have escaped the tutorial', mode=COMPLETE) # allows warp
# ,
# TODO convert this to a separate quest (in bits 28-30)
# Slice('STARTAREA', 0, 4).states('Attitude Adjustment')
(9, 'You noticed Hasan threating someone')
(10, "Kaan will help if you can discover Hasan's weakness")
(11, 'Tell Kaan that Hasan is afraid of scorpions')
(12, 'Kaan will summon a scorpion while you talk to Hasan')
(13, "You killed the scorpion threatening Hasan. Maybe he'll think differently about you now")
(14, "You sure taught Hasan a lesson he didn't expect", mode=COMPLETE)
,
Slice('STARTAREA', 4, 4).states('Pest Control')
(1, 'Valon needs help at the gate', mode=KNOWN)
(2, 'Kill 10 Maggots and then report back to Valon')
(3, 'Kill 5 House Maggots and then report back to Valon')
(4, 'Kill 3 Tame Scorpions and then report back to Valon')
(5, 'Kill 1 Scorpion and then report back to Valon')
(6, 'You have killed enough monsters for Valon', mode=COMPLETE)
,
Slice('STARTAREA', 8, 4).counter('##BPest Control##b mobs killed').condition('2 <= {0} && {0} <= 5'.format(Slice('STARTAREA', 4, 4).expr()))
,
Slice('STARTAREA', 12, 4).states('MIT: Intro')
(1, 'Morgan has offered to each you magic (requires 5+ Int)', mode=KNOWN)
(2, 'Morgan wants you to demonstrate the #confringo spell')
(3, 'Tell Morgan that you successfully cast #confringo')
(4, 'You have learned the basics of magic', mode=COMPLETE)
,
Slice('STARTAREA', 16, 4).states('Barrels O\' Fun!')
(1, 'Zegas needs some help with barrels in the storeroom', mode=KNOWN)
(2, 'Search the barrels in the storeroom')
(3, 'You found a Bug Bomb in the storeroom. Talk to Zegas')
(4, 'You searched all the barrels for Zegas', mode=COMPLETE)
,
Slice('STARTAREA', 20).flag('barrel 1 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 21).flag('barrel 2 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 22).flag('barrel 3 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 23).flag('barrel 4 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 24).flag('barrel 5 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 25).flag('barrel 6 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 26).flag('barrel 7 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 27).flag('barrel 8 searched').condition('%s == 2' % Slice('STARTAREA', 16, 4).expr())
,
Slice('STARTAREA', 28, 3).reserved('Attitude Adjustment')
,
Slice('STARTAREA', 31).flag('Talked to Kaan')
,

Slice('MAGIC_CAST_TICK').ignored()
,
Slice('HALLOWEENTIME', 0, 16).counter('Bad Karma')
,
]


if __name__ == '__main__':
    main()
