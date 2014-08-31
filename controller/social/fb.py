from bottle import get, request
import urllib
from passwd import *
import json
from model import User
from ..utils import *
from collections import defaultdict


def fb_get_url(redirect):
    param = { 'client_id': fb_client_id, 
              'response_type': 'code',
              'redirect_uri': REDIRECT_URI + redirect
            }
    data = urllib.parse.urlencode(param)
    fb_url = 'https://www.facebook.com/dialog/oauth?' + data
    return fb_url

def fb_get_access_token(code, redirect):
    param = { 'redirect_uri': REDIRECT_URI + redirect,
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
    access_token = fb_get_access_token(code, '/fblogin')

    resp = fb_get_user_info(access_token)

    user = User.objects(fb_id=resp['id']).first()
    if user is not None:
        return log_in_user(user)


    s = request.environ.get('beaker.session')
    user = defaultdict(str)
    user['first_name'] = resp['first_name']
    user['last_name'] = resp['last_name']
    user['email'] = resp['email']
    user['uid'] = "fb:" + resp['id']
    s['user.data'] = user

    redirect('/register')


@get('/fbconnect')
@require_login()
def connect_fb(user):
    code = request.query.get("code")
    access_token = fb_get_access_token(code, '/fbconnect')
    resp = fb_get_user_info(access_token)
    user['fb_id'] = resp['id']    

    user.save()
    redirect('/account')

@get('/fbdisconnect')
@require_login()
def disconnetc_fb(user):
    user['fb_id'] = ''
    user.save()
    redirect('/account')
