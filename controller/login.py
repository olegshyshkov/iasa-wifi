__author__ = 'olage'

from bottle import route, view, run
from bottle import request, response, redirect
from bcrypt import hashpw, gensalt

from model import Session, User
from .utils import *




from bottle import run, route, request, view, static_file, get, post, response, redirect
import os
import urllib.request
import urllib.parse
import json
from collections import defaultdict
from model import User, PersonalInfo, Session
import random


vk_client_id = '4526628'
vk_client_secret = 'zvuvIauM6b134uaztW5J'
fb_client_id = '308008439382079'
fb_client_secret = '3ef8716e5917d712f34e3b4d3d78e83d'

g_client_id = '948626997446-gper9q4qb6knlfnqhaoggqlm7kjvcjbf.apps.googleusercontent.com'
g_client_secret = 'sctFheKq_0nuSrApn05KPKgg'

#REDIRECT_URI = 'http://192.168.25.42:8080/vklogin'
REDIRECT_URI = 'http://localhost:8080' 
#REDIRECT_URI = "https://oauth.vk.com/blank.html"
#.encode('utf-8')


@route('/')
def root():
    redirect('/login')

@route('/login')
@view('login')
@require_login(on_login=True)
def greet():
    param = { 'client_id': vk_client_id, 
              'response_type': 'code',
              'redirect_uri': REDIRECT_URI + '/vklogin'
            }

    data = urllib.parse.urlencode(param)
    vkurl = "http://oauth.vk.com/authorize?" + data

    param = { 'client_id': fb_client_id, 
              'response_type': 'code',
              'redirect_uri': REDIRECT_URI + '/fblogin'
            }
    data = urllib.parse.urlencode(param)
    fburl = 'https://www.facebook.com/dialog/oauth?' + data
    

    param = { 'client_id': g_client_id, 
              'response_type': 'code',
              'redirect_uri': REDIRECT_URI + '/glogin',
              'scope': 'email'
            }

    data = urllib.parse.urlencode(param)
    gurl = "https://accounts.google.com/o/oauth2/auth?" + data

    return {'vkurl': vkurl, 'fburl': fburl, 'gurl': gurl, 'err': ""}


@route('/passlogin', method='POST')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')

    user = User.objects(username=username).first()
    if user is None:
        return login('Wrong login or password')

#    print(user['username'], user['password'], hashpw(password.encode('utf-8'), user['password'])) # .encode('utf-8')))
#    print(user['username'], user['password'], hashpw(password.encode('utf-8'), user.password)) # .encode('utf-8')))

    if user.is_good_password(password):
        start_session(user)
        redirect('account')
    else:
        return login('Wrong login or password')

def start_session(user):
    session = Session(username=user['username'], user=user, session_id=hex(random.getrandbits(128))).save()
    response.set_cookie('session', str(session.id))


def log_in_user(user):
    start_session(user)
    redirect('account')

#@route('/enter/VK', method='GET')


def vk_get_access_token(code):
    param = { 'redirect_uri': REDIRECT_URI + '/vklogin',
              'client_id': vk_client_id, 
              'client_secret': vk_client_secret, 
              'code': code             
            }
    
    data = urllib.parse.urlencode(param)
    url = "https://oauth.vk.com/access_token?" + data
    f = urllib.request.urlopen(url)
    s = f.read().decode("utf-8")
    js = json.loads(s)

    user_id = js['user_id']
    access_token = js['access_token']
    return (user_id, access_token)

def vk_get_user_info(user_id, access_token):
    param = {   'user_id': user_id, 
                'access_token': access_token,
                'fields': 'uid,first_name,last_name,contacts'
            }

    data = urllib.parse.urlencode(param)
    url = "https://api.vk.com/method/users.get?" + data
    f = urllib.request.urlopen(url)
    s = f.read().decode("utf-8")
    js = json.loads(s)
    
    resp = js['response'][0]
    return resp

@get('/vklogin')
def enter_vk():
    code = request.query.get("code")
    user_id, access_token = vk_get_access_token(code)

    user = User.objects(vk_id=str(user_id)).first()
    if user is not None:
        return log_in_user(user)
    
    resp = vk_get_user_info(user_id, access_token)    
    
    user = defaultdict(str)
    user['first_name'] = resp['first_name']
    user['last_name'] = resp['last_name']
    return edit(user, "vk:" + str(user_id))

    #return str(js['user_id'])


def fb_get_access_token(code):
    param = { 'redirect_uri': REDIRECT_URI + '/fblogin',
              'client_id': fb_client_id, 
              'client_secret': fb_client_secret, 
              'code': code             
            }
   
    data = urllib.parse.urlencode(param)
    url = "https://graph.facebook.com/oauth/access_token?" + data
    f = urllib.request.urlopen(url)
    s = f.read().decode('utf-8')
    s = {k: v for (k, v) in [t.split('=') for t in s.split('&')]}
    
    access_token = s['access_token']
    return access_token


def fb_get_user_info(access_token):
    url = 'https://graph.facebook.com/me?access_token=' + access_token
    f = urllib.request.urlopen(url)
    s = f.read().decode('utf-8')
    resp = json.loads(s)
    return resp


@get('/fblogin')
def enter_fb():
    code = request.query.get("code")
    access_token = fb_get_access_token(code)

    resp = fb_get_user_info(access_token)

    user = User.objects(fb_id=resp['id']).first()
    if user is not None:
        return log_in_user(user)

    user = defaultdict(str)
    user['first_name'] = resp['first_name']
    user['last_name'] = resp['last_name']
    user['email'] = resp['email']
    return edit(user, "fb:" + resp['id'])    
    #return res


def g_get_access_token(code):
    param = { 'redirect_uri': REDIRECT_URI + '/glogin',
              'client_id': g_client_id, 
              'client_secret': g_client_secret, 
              'code': code,
              'grant_type': 'authorization_code'
            }
   
    data = urllib.parse.urlencode(param).encode('utf-8')
    url = "https://accounts.google.com/o/oauth2/token"
    f = urllib.request.urlopen(url, data)
    s = f.read().decode('utf-8')
    res = json.loads(s)
    access_token = res['access_token']
    return access_token

def g_get_user_info(access_token):
    url = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token
    f = urllib.request.urlopen(url)
    s = f.read().decode('utf-8')
    resp = json.loads(s)
    return resp

@get('/glogin')
def enter_g():
    code = request.query.get("code")
    access_token = g_get_access_token(code)
    resp = g_get_user_info(access_token)
 
    user = User.objects(g_id=resp['id']).first()
    if user is not None:
        return log_in_user(user)

    user = defaultdict(str)
    user['first_name'] = resp['given_name']
    user['last_name'] = resp['family_name']
    user['email'] = resp['email']
    return edit(user, "g:" + resp['id'])

    
@route('/edit')
@view("edit.html")
def edit(user={"login":""}, uid=""):
    return {"user": user, "uid": uid}

def check_login(username):
    return True

def check_password(p1, p2):
    return True


@post('/user/save')
def user_save():
    user = User()
    user.from_request(request)

    if not check_login(user['username']):
        return register_view(err="Wrong login" + user['username'])

    pass1 = request.forms.get('password1')
    pass2 = request.forms.get('password2')

    if not check_password(pass1, pass2):
        return register_view(err="Wrong password '" + pass1 + "' '" + pass2 + "'")

    
    user.save()

    redirect('/account')


@route('/jquery-2.1.1.min.js', name='static')
def style():
    return static_file("jquery-2.1.1.min.js", root='')

@route('/logined')
def logined(name, age):
    return name + " " + age

@route('/account')
def account():
    return "Account"


@route('/login', method='POST')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')

    user = User.objects(username=username).first()
    if user is None:
        return login('Wrong login or password')

#    print(user['username'], user['password'], hashpw(password.encode('utf-8'), user['password'])) # .encode('utf-8')))
    print(user['username'], user['password'], hashpw(password.encode('utf-8'), user.password)) # .encode('utf-8')))

    if user.is_good_password(password):
        start_session(user)
        redirect('account')
    else:
        return login('Wrong login or password')

@route('/logout')
def logout():
    cookie = request.get_cookie("session")
    session = Session.objects(id=cookie).delete()
    redirect('/login')

@route('/register')
@view('register')
def register_view(err=''):
    return {'err': err}

@route('/register', method='POST')
def register_post():
    user = user_from_form(request.forms)

    if not check_login(user['username']):
        return register_view(err="Wrong login" + user['username'])

    pass1 = request.forms.get('password1')
    pass2 = request.forms.get('password2')

    if not check_password(pass1, pass2):
        return register_view(err="Wrong password '" + pass1 + "' '" + pass2 + "'")

    user.password = hashpw(pass1.encode('utf-8'), gensalt(10))
    user.save()

    redirect('/account')
