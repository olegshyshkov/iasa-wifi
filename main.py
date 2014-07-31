#!/usr/bin/env python3

import os
import sys

from bottle import run, route, view, redirect
from bottle import template, request, static_file
from controller import login, user, admin


@route('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name}}, how are you?', name=name)

@route('/style.css', name='static')
def style():
	return static_file("style.css", root='')

if __name__ == "__main__":
    #run(host='localhost', port=8080, debug=True, reloader=True)
    #run(host='192.168.0.100', port=45845, debug=True, reloader=True)
    #run(host='10.35.7.10', port=8080, debug=True, reloader=True)
    #run(host='192.168.0.104', port=8080, debug=True, reloader=True)
    run(host='127.0.0.1', port=8080, debug=True, reloader=True)
    #run(host='192.168.0.11', port=8080, debug=True, reloader=True)
    #run(host='178.150.0.61', port=8080, debug=True, reloader=True)
