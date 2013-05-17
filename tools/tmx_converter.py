#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    tmx_converter.py - Extract walkmap, warp, and spawn information from maps.
##
##    Copyright © 2012 Ben Longbons <b.r.longbons@gmail.com>
##
##    This file is part of The Mana World
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import sys
import os
import posixpath
import struct
import xml.sax
import base64
import zlib

dump_all = False # wall of text
check_mobs = True # mob_db.txt

# lower case versions of everything except 'spawn' and 'warp'
other_object_types = set([
    'particle_effect',
    'npc', # not interpreted by client
    'script', # for ManaServ
    'fixme', # flag for things that didn't have a type before
])

# Somebody has put ManaServ fields in our data!
other_spawn_fields = (
    'spawn_rate',
)
other_warp_fields = (
)

TILESIZE = 32
SEPARATOR = '|'
MESSAGE = 'This file is generated automatically. All manually changes will be removed when running the Converter.'
CLIENT_MAPS = 'maps'
SERVER_WLK = 'data'
SERVER_NPCS = 'npc'
SERVER_MOB_DB = 'db/mob_db.txt'
NPC_MOBS = '_mobs.txt'
NPC_WARPS = '_warps.txt'
NPC_IMPORTS = '_import.txt'
NPC_MASTER_IMPORTS = NPC_IMPORTS

class State(object):
    pass
State.INITIAL = State()
State.LAYER = State()
State.DATA = State()
State.FINAL = State()

class Object(object):
    __slots__ = (
        'name',
        #'map',
        'x', 'y',
        'w', 'h',
    )
class Mob(Object):
    __slots__ = (
        'monster_id',
        'max_beings',
        'ea_spawn',
        'ea_death',
    ) + other_spawn_fields
    def __init__(self):
        self.max_beings = 1
        self.ea_spawn = 0
        self.ea_death = 0

class Warp(Object):
    __slots__ = (
        'dest_map',
        'dest_x',
        'dest_y',
    ) + other_warp_fields

class ContentHandler(xml.sax.ContentHandler):
    __slots__ = (
        'locator',  # keeps track of location in document
        'out',      # open file handle to .wlk
        'state',    # state of collision info
        'tilesets', # first gid of each tileset
        'buffer',   # characters within a section
        'encoding', # encoding of layer data
        'compression', # compression of layer data
        'width',    # width of the collision layer
        'height',   # height of the collision layer
        'base',     # base name of current map
        'npc_dir',  # world/map/npc/<base>
        'mobs',     # open file to _mobs.txt
        'warps',    # open file to _warps.txt
        'imports',  # open file to _import.txt
        'name',     # name property of the current map
        'object',   # stores properties of the latest <object> tag
        'mob_ids',  # set of all mob types that spawn here
    )
    def __init__(self, out, npc_dir, mobs, warps, imports):
        xml.sax.ContentHandler.__init__(self)
        self.locator = None
        self.out = open(out, 'w')
        self.state = State.INITIAL
        self.tilesets = set([0]) # consider the null tile as its own tileset
        self.buffer = bytearray()
        self.encoding = None
        self.compression = None
        self.width = None
        self.height = None
        self.base = posixpath.basename(npc_dir)
        self.npc_dir = npc_dir
        self.mobs = mobs
        self.warps = warps
        self.imports = imports
        self.object = None
        self.mob_ids = set()

    def setDocumentLocator(self, loc):
        self.locator = loc

    # this method randomly cuts in the middle of a line; thus funky logic
    def characters(self, s):
        if not s.strip():
            return
        if self.state is State.DATA:
            self.buffer += s.encode('ascii')

    def startDocument(self):
        pass

    def startElement(self, name, attr):
        if dump_all:
            attrs = ' '.join('%s="%s"' % (k,v) for k,v in attr.items())
            if attrs:
                print('<%s %s>' % (name, attrs))
            else:
                print('<%s>' % name)

        if self.state is State.INITIAL:
            if name == u'property' and attr[u'name'].lower() == u'name':
                self.name = attr[u'value']
                self.mobs.write('// %s\n' % MESSAGE)
                self.mobs.write('// %s mobs\n\n' % self.name)
                self.warps.write('// %s\n' % MESSAGE)
                self.warps.write('// %s warps\n\n' % self.name)

            if name == u'tileset':
                self.tilesets.add(int(attr[u'firstgid']))

            if name == u'layer' and attr[u'name'].lower().startswith(u'collision'):
                self.width = int(attr[u'width'])
                self.height = int(attr[u'height'])
                self.out.write(struct.pack('<HH', self.width, self.height))
                self.state = State.LAYER
        elif self.state is State.LAYER:
            if name == u'data':
                if attr.get(u'encoding','') not in (u'', u'csv', u'base64', u'xml'):
                    print('Bad encoding:', attr.get(u'encoding',''))
                    return
                self.encoding = attr.get(u'encoding','')
                if attr.get(u'compression','') not in (u'', u'none', u'zlib', u'gzip'):
                    print('Bad compression:', attr.get(u'compression',''))
                    return
                self.compression = attr.get(u'compression','')
                self.state = State.DATA
        elif self.state is State.DATA:
            self.out.write(chr(int(attr.get(u'gid',0)) not in self.tilesets))
        elif self.state is State.FINAL:
            if name == u'object':
                obj_type = attr[u'type'].lower()
                x = int(attr[u'x']) / TILESIZE;
                y = int(attr[u'y']) / TILESIZE;
                w = int(attr.get(u'width', 0)) / TILESIZE;
                h = int(attr.get(u'height', 0)) / TILESIZE;
                # I'm not sure exactly what the w/h shrinking is for,
                # I just copied it out of the old converter.
                # I know that the x += w/2 is to get centers, though.
                if obj_type == 'spawn':
                    self.object = Mob()
                    if w > 1:
                        w -= 1
                    if h > 1:
                        h -= 1
                    x += w/2
                    y += h/2
                elif obj_type == 'warp':
                    self.object = Warp()
                    x += w/2
                    y += h/2
                    w -= 2
                    h -= 2
                else:
                    if obj_type not in other_object_types:
                        print('Unknown object type:', obj_type, file=sys.stderr)
                    self.object = None
                    return
                obj = self.object
                obj.x = x
                obj.y = y
                obj.w = w
                obj.h = h
                obj.name = attr[u'name']
            elif name == u'property':
                obj = self.object
                if obj is None:
                    return
                key = attr[u'name'].lower()
                value = attr[u'value']
                # Not true due to defaulting
                #assert not hasattr(obj, key)
                try:
                    value = int(value)
                except ValueError:
                    pass
                setattr(obj, key, value)

    def add_warp_line(self, line):
        self.warps.write(line)

    def endElement(self, name):
        if dump_all:
            print('</%s>' % name)

        if name == u'object':
            obj = self.object
            if isinstance(obj, Mob):
                mob_id = obj.monster_id
                if mob_id < 1000:
                    mob_id += 1002
                if check_mobs:
                    try:
                        name = mob_names[mob_id]
                    except KeyError:
                        print('Warning: unknown mob ID: %d (%s)' % (mob_id, obj.name))
                    else:
                        if name != obj.name:
                            print('Warning: wrong mob name: %s (!= %s)' % (obj.name, name))
                            obj.name = name
                self.mob_ids.add(mob_id)
                self.mobs.write(
                    SEPARATOR.join([
                        '%s.gat,%d,%d,%d,%d' % (self.base, obj.x, obj.y, obj.w, obj.h),
                        'monster',
                        obj.name,
                        '%d,%d,%d,%d,Mob%s::On%d\n' % (mob_id, obj.max_beings, obj.ea_spawn, obj.ea_death, self.base, mob_id),
                    ])
                )
            elif isinstance(obj, Warp):
                self.warps.write(
                    SEPARATOR.join([
                        '%s.gat,%d,%d' % (self.base, obj.x, obj.y),
                        'warp',
                        obj.name,
                        '%d,%d,%s.gat,%d,%d\n' % (obj.w, obj.h, obj.dest_map, obj.dest_x / 32, obj.dest_y / 32),
                    ])
                )

        if name == u'data':
            if self.state is State.DATA:
                if self.encoding == u'csv':
                    for x in self.buffer.split(','):
                        self.out.write(chr(int(x) not in self.tilesets))
                elif self.encoding == u'base64':
                    data = base64.b64decode(str(self.buffer))
                    if self.compression == u'zlib':
                        data = zlib.decompress(data)
                    elif self.compression == u'gzip':
                        data = zlib.decompressobj().decompress('x\x9c' + data[10:-8])
                    for i in range(self.width*self.height):
                        self.out.write(chr(int(struct.unpack('<I',data[i*4:i*4+4])[0]) not in self.tilesets))
                self.state = State.FINAL

    def endDocument(self):
        self.mobs.write('\n\n%s.gat,0,0,0|script|Mob%s|-1,{\n' % (self.base, self.base))
        for mob_id in sorted(self.mob_ids):
            self.mobs.write('On%d:\n    set @mobID, %d;\n    callfunc "MobPoints";\n    end;\n\n' % (mob_id, mob_id))
        self.mobs.write('    end;\n}\n')
        self.imports.write('// Map %s: %s\n' % (self.base, self.name))
        self.imports.write('// %s\n' % MESSAGE)
        self.imports.write('map: %s.gat\n' % self.base)

        npcs = os.listdir(self.npc_dir)
        npcs.sort()
        for x in npcs:
            if x == NPC_IMPORTS:
                continue
            if x.startswith('.'):
                continue
            if x.endswith('.txt'):
                self.imports.write('npc: %s\n' % posixpath.join(SERVER_NPCS, self.base, x))
        pass

def main(argv):
    _, client_data, server_data = argv
    tmx_dir = posixpath.join(client_data, CLIENT_MAPS)
    wlk_dir = posixpath.join(server_data, SERVER_WLK)
    npc_dir = posixpath.join(server_data, SERVER_NPCS)
    if check_mobs:
        global mob_names
        mob_names = {}
        with open(posixpath.join(server_data, SERVER_MOB_DB)) as mob_db:
            for line in mob_db:
                if not line.strip():
                    continue
                if line.startswith('#'):
                    continue
                if line.startswith('//'):
                    continue
                k, v, _ = line.split(',', 2)
                mob_names[int(k)] = v.strip()

    npc_master = []
    map_basenames = []

    for arg in os.listdir(tmx_dir):
        base, ext = posixpath.splitext(arg)

        if ext == '.tmx':
            map_basenames.append(base)
            tmx = posixpath.join(tmx_dir, arg)
            wlk = posixpath.join(wlk_dir, base + '.wlk')
            this_map_npc_dir = posixpath.join(npc_dir, base)
            os.path.isdir(this_map_npc_dir) or os.mkdir(this_map_npc_dir)
            print('Converting %s to %s' % (tmx, wlk))
            with open(posixpath.join(this_map_npc_dir, NPC_MOBS), 'w') as mobs:
                with open(posixpath.join(this_map_npc_dir, NPC_WARPS), 'w') as warps:
                    with open(posixpath.join(this_map_npc_dir, NPC_IMPORTS), 'w') as imports:
                        xml.sax.parse(tmx, ContentHandler(wlk, this_map_npc_dir, mobs, warps, imports))
            npc_master.append('import: %s\n' % posixpath.join(SERVER_NPCS, base, NPC_IMPORTS))

    with open(posixpath.join(wlk_dir, 'resnametable.txt'), 'w') as resname:
        for base in sorted(map_basenames):
            resname.write('%s.gat#%s.wlk#\n' % (base, base))
    with open(posixpath.join(npc_dir, NPC_MASTER_IMPORTS), 'w') as out:
        out.write('// %s\n\n' % MESSAGE)
        npc_master.sort()
        for line in npc_master:
            out.write(line)

if __name__ == '__main__':
    main(sys.argv)
