__author__ = 'olage'

from bottle import route, view, run
from bottle import request, response, redirect
from bcrypt import hashpw, gensalt

from model import User
from .utils import *
from passwd import *



from bottle import run, route, request, view, static_file, get, post, response, redirect
import bottle
import os
import urllib.request
import urllib.parse
import json
from collections import defaultdict
from model import User, PersonalInfo
import random

from .social import fb, vk, g

@route('/')
def root():
    redirect('/login')

@route('/login')
@view('login')
@require_login(on_login=True)
def greet():
    s = request.environ.get('beaker.session')
    errors = s.get("login_errors", "")
    s["login_errors"] = ""

    vkurl = vk.vk_get_url('/vklogin')
    fburl =  fb.fb_get_url('/fblogin')
    gurl = g.g_get_url('/glogin')

    return {'vkurl': vkurl, 'fburl': fburl, 'gurl': gurl, 'err': errors}


@route('/passlogin', method='POST')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')

    s = request.environ.get('beaker.session')

    user = User.objects(username=username).first()
    if user is None:
        s["login_errors"] = 'Wrong login or password'
        redirect('/login')

    if user.is_good_password(password):
        start_session(user)
        redirect('account')
    else:
        s["login_errors"] = 'Wrong login or password'
        redirect('/login')



@route('/logout')
def logout():
    s = request.environ.get('beaker.session')
    if "user.username" in s:
        del s["user.username"]
    redirect('/login')

