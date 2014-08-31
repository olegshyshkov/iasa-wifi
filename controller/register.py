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


@route('/register')
@view('register')
def register_view():
    s = request.environ.get('beaker.session')

    data = s.get("user.data", defaultdict(str))
    errors = s.get('errors', [])

    return {"user": data, "errors": errors}

@post('/user/save')
@view('register')
def register():
    s = request.environ.get('beaker.session')
    data = s.get('user.data', defaultdict(str))
    print(data)
    for key in ['username', 'first_name', 'last_name', 'middle_name', 'study_group', 
                'email', 'phone_number', 'skype', 'icq', 'password1', 'password2']:
        data[key] = request.forms.get(key).encode("ISO-8859-1").decode("utf-8")
        

    print(data)
     
    errors = []

    if "errors" in s:
        del s["errors"]
    if "user.data" in s:
        del s['user.data'] 

    user = User.objects(username=data['username']).first()

    if user is not None:
        errors.append('Login is already in use')

    if data['password1'] != data['password2']:
        errors.append("Passwords don't match")

    if data['password1'] == '':
        errors.append('Password required')

    if data['first_name'] == '':
        errors.append('First name is required')

    if data['last_name'] == '':
        errors.append('Last name is required')


    if len(errors) == 0:
        user = User()
        user.from_dict(data)
        user.save()
        start_session(user)

        redirect('/account')
    else:
        print(errors)

        s["user.data"] = data
        s["errors"] = errors
        redirect('/register')