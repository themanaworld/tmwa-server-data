#!/usr/bin/env python2.6

from flask import Flask

from with_xml import Node

app = Flask(__name__)

@app.route('/')
def index():
    content = Node()
    tag = content.tag
    put = content.put
    a = tag('a')
    with tag('html'):
        with tag('head'):
            with tag('title'):
                put('Title')
        with tag('body'):
            with tag('h1'):
                put('Header')
            put('This is ')
            with a(href='http://google.com/'):
                put('a link to Google.')
    return str(content)

if __name__ == '__main__':
    app.run(debug=True)
