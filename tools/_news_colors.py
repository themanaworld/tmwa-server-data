#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    _news_colors.py - colors that can be used in news
##
##    Copyright © 2012 Ben Longbons <b.r.longbons@gmail.com>
##
##    This file is part of The Mana World (Athena server)
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

import cgi

__all__ = ['make_html_colors_dict', 'make_txt_colors_dict']

class Color(object):
    __slots__ = ('txt', 'rgb')
    def __init__(self, txt, rgb):
        self.txt = txt
        self.rgb = rgb

color_dict = dict(
    black  = Color(txt='##0', rgb=0x000000),
    red    = Color(txt='##1', rgb=0xff0000),
    green  = Color(txt='##2', rgb=0x009000),
    blue   = Color(txt='##3', rgb=0x0000ff),
    orange = Color(txt='##4', rgb=0xe0980e),
    yellow = Color(txt='##5', rgb=0xf1dc27),
    pink   = Color(txt='##6', rgb=0xff00d8),
    purple = Color(txt='##7', rgb=0x8415e2),
    gray   = Color(txt='##8', rgb=0x919191),
    brown  = Color(txt='##9', rgb=0x8e4c17),
)

class HtmlDate(object):
    __slots__ = ()
    def __format__(self, date):
        return '<font color="#0000ff">%s</font>' % date

class HtmlLink(object):
    __slots__ = ()
    def __format__(self, target):
        target = cgi.escape(target, True)
        return '<a href="%s">%s</a>' % (target, target)

class HtmlSignature(object):
    __slots__ = ()
    def __format__(self, author):
        return '-<font color="#009000">%s</font>' % author

def make_html_colors_dict():
    r = {
        'date': HtmlDate(),
        'link': HtmlLink(),
        'author': HtmlSignature(),
    }
    for k, v in color_dict.items():
        r[k] = '<font color="#%06x">' % v.rgb
        r['/' + k] = '</font>'
    return r

# Here be dragons

def make_txt_colors_dict():
    return dict(generate_txt_colors())

class StackPusher(object):
    __slots__ = ('stack', 'txt')
    def __init__(self, stack, txt):
        self.stack = stack
        self.txt = txt
    def __format__(self, fmt):
        assert fmt == ''
        txt = self.txt
        self.stack.append(txt)
        return txt

class StackPopper(object):
    __slots__ = ('stack', 'txt')
    def __init__(self, stack, txt):
        self.stack = stack
        self.txt = txt
    def __format__(self, fmt):
        assert fmt == ''
        txt = self.txt
        if len(self.stack) <= 1:
            raise SyntaxError('Unmatched {/%s}' % txt)
        prev = self.stack.pop()
        if txt != prev:
            raise SyntaxError('Mismatched {/%s} from {%s}' % (txt, prev))
        return self.stack[-1]

class TxtDate(object):
    __slots__ = ('stack')
    def __init__(self, stack):
        self.stack = stack
    def __format__(self, date):
        return '##3' + date + self.stack[-1]

class TxtLink(object):
    __slots__ = ('stack')
    def __init__(self, stack):
        self.stack = stack
    def __format__(self, target):
        # the field labeled 'bug' should not be necessary ...
        return '@@{link}|{text}@@{bug}'.format(link=target, text=target, bug=self.stack[-1])

class TxtSignature(object):
    __slots__ = ('stack')
    def __init__(self, stack):
        self.stack = stack
    def __format__(self, author):
        return '-##2' + author + self.stack[-1]

def generate_txt_colors():
    stack = ['##0'] # don't let stack become empty
    for k,v in color_dict.items():
        yield k, StackPusher(stack, v.txt)
        yield '/' + k, StackPopper(stack, v.txt)
    yield 'date', TxtDate(stack)
    yield 'link', TxtLink(stack)
    yield 'author', TxtSignature(stack)
