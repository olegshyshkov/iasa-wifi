from bottle import get, request
import urllib
from passwd import *
import json
from model import User
from ..utils import *
from collections import defaultdict



def vk_get_url(redirect):
    param = { 'client_id': vk_client_id, 
              'response_type': 'code',
              'redirect_uri': REDIRECT_URI + redirect
            }

    data = urllib.parse.urlencode(param)
    vkurl = "http://oauth.vk.com/authorize?" + data

    return vkurl

def vk_get_access_token(code, redirect):
    param = { 'redirect_uri': REDIRECT_URI + redirect,
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
    user_id, access_token = vk_get_access_token(code, '/vklogin')

    user = User.objects(vk_id=str(user_id)).first()
    if user is not None:
        return log_in_user(user)
    
    resp = vk_get_user_info(user_id, access_token)
    
    s = request.environ.get('beaker.session')

    user = defaultdict(str)
    user['first_name'] = resp['first_name']
    user['last_name'] = resp['last_name']
    user['uid'] = "vk:" + str(user_id)
    s['user.data'] = user
    
    redirect('/register')


@get('/vkconnect')
@require_login()
def connect_fb(user):
    code = request.query.get("code")
    user_id, access_token = vk_get_access_token(code, '/vkconnect')
    user['vk_id'] = str(user_id)

    user.save()
    redirect('/account')


@get('/vkdisconnect')
@require_login()
def disconnetc_fb(user):
    user['vk_id'] = ''
    user.save()
    redirect('/account')
