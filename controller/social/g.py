from bottle import get, request
import urllib
from passwd import *
import json
from model import User
from ..utils import *
from collections import defaultdict


def g_get_url(redirect):
    param = { 'client_id': g_client_id, 
              'response_type': 'code',
              'redirect_uri': REDIRECT_URI + redirect,
              'scope': 'email'
            }

    data = urllib.parse.urlencode(param)
    g_url = "https://accounts.google.com/o/oauth2/auth?" + data
    return g_url

def g_get_access_token(code, redirect):
    param = { 'redirect_uri': REDIRECT_URI + redirect,
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
    access_token = g_get_access_token(code, '/glogin')
    resp = g_get_user_info(access_token)
 
    user = User.objects(g_id=resp['id']).first()
    if user is not None:
        return log_in_user(user)

    s = request.environ.get('beaker.session')

    user = defaultdict(str)
    user['first_name'] = resp['given_name']
    user['last_name'] = resp['family_name']
    user['email'] = resp['email']
    user['uid'] = "g:" + resp['id']
    s['user.data'] = user
    
    redirect('/register')


@get('/gconnect')
@require_login()
def connect_fb(user):
    code = request.query.get("code")
    access_token = g_get_access_token(code, '/gconnect')
    resp = g_get_user_info(access_token)
    user['g_id'] = resp['id']    

    user.save()
    redirect('/account')


@get('/gdisconnect')
@require_login()
def disconnetc_fb(user):
    user['g_id'] = ''
    user.save()
    redirect('/account')
