''' A stupid little way of generating xml
'''

import re

from flask import escape

PRETTY = True

class Context(object):
    __slots__ = ('_node', '_name', '_kwargs')
    pattern = re.compile(r'[A-Za-z]\w*')

    def __init__(self, node, name, kwargs):
        self._node = node
        self._name = name
        self._kwargs = kwargs

    def __enter__(self):
        _node = self._node
        _buffer = _node._buffer
        _node.nl()
        _buffer.extend(['<', escape(self._name)])
        for k, v in self._kwargs.iteritems():
            assert Context.pattern.match(k)
            _buffer.extend([' ', k, '="', escape(v), '"'])
        _buffer.append('>')
        _node._indent += 1
        _node.nl()

    def __exit__(self, exc_type, exc_value, traceback):
        _node = self._node
        _buffer = _node._buffer
        _node._indent -= 1
        _node.nl()
        if _buffer[-1] == '>' and _buffer[-3] != '</':
            _buffer[-1] = '/>'
        else:
            _buffer.extend(['</', escape(self._name), '>'])
        _node.nl()

    def __call__(_self, **kwargs):
        new_kwargs = dict(_self._kwargs)
        new_kwargs.update(kwargs)
        return Context(_self._node, _self._name, new_kwargs)

class Node(object):
    __slots__ = ('_buffer', '_indent')

    def __init__(self):
        self._buffer = ['<?xml version="1.0" encoding="utf-8"?>', '\n', '']
        self._indent = 0

    def tag(_self, _name, **kwargs):
        return Context(_self, _name, kwargs)


    def put(self, text):
        self._buffer.append(escape(text))

    def __str__(self):
        return ''.join(self._buffer)

    def nl(self):
        if PRETTY:
            _buffer = self._buffer
            if _buffer[-2] == '\n':
                _buffer.pop()
            else:
                _buffer.append('\n')
            _buffer.extend(['  ' * self._indent])
