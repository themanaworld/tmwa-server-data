#!/usr/bin/env python
#
#       showmagicspells.py
#
#       Copyright 2010 Stefan Beller
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

def handle_lines(lines):
    def getInfo(line, info):
        sp = line.split(" ")
        if info in sp:
            pos = sp.index(info)
            return sp[pos+2].strip()
        return ""

    firstline = lines[0].split(" ")
    pos=firstline.index("SPELL")
    name= firstline[pos+1]
    level = getInfo(lines[1],"level")
    school = getInfo(lines[2],"school")

    #print name,level,school
    if not school in spells:
        spells[school]=[]
    spells[school]+=[(name,level,school)]

def main():
    fname = "../conf/magic.conf.template"
    f=open(fname, "r");
    lines=f.readlines();
    f.close();

    while lines :
        line=lines[0]
        if line.startswith("SPELL"):
            handle_lines(lines);
        if line.startswith("# LOCAL SPELL"):
            handle_lines(lines);
        if line.startswith("# SPELL"):
            handle_lines(lines);
        del lines[0]
    return 0

spells={}
main()
for x in spells:
    print x
    for y in spells[x]:
        print "\t",y[1],y[0];

