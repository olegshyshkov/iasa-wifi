__author__ = 'olage'

from bottle import run, route, view, redirect
from bottle import template, request
from controller.login import require_login

from model import User, Device, DHCPLease
import string

from .utils import *
from .social import fb, vk, g

def get_user_mac():
    ip = request['REMOTE_ADDR']
    dhcp = DHCPLease.objects(ip=ip).first()
    if dhcp is not None:
        mac = dhcp.mac
    else:
        mac = None
    return mac


@route('/account')
@view('user/account')
@require_login()
def account_view(user):
    mac = get_user_mac()  
    

    if user.fb_id == '':
        fb_name, fb_url = ("Connect with facebook", fb.fb_get_url('/fbconnect'))
    else:
        fb_name, fb_url = ("Disconect from facebook", '/fbdisconnect')


    if user.g_id == '':
        g_name, g_url = ("Connect with google", g.g_get_url('/gconnect'))
    else:
        g_name, g_url = ("Disconect from google", '/gdisconnect')


    if user.vk_id == '':
        vk_name, vk_url = ("Connect with vk", vk.vk_get_url('/vkconnect'))
    else:
        vk_name, vk_url = ("Disconect from vk", '/vkdisconnect')


    #return dhcp.ip + " " + dhcp.mac
    return {'username': user.username,
            'group': user.group.name,
            'name': user.personal.first_name + " " + user.personal.last_name,
            'study_group': user.personal.study_group,
            'devices': user.devices, 
            'mac': mac,
            'user': user,
            'fb_url': fb_url, 'fb_name': fb_name,
            'g_url': g_url, 'g_name': g_name,
            'vk_url': vk_url, 'vk_name': vk_name}

@route('/add_device', method='post')
@require_login()
def account_post(user):
    mac = request.forms.get('mac')
    if mac is None:
        mac = get_user_mac()
        #redirect('/account')
    mac = format_mac(mac)
    typ = request.forms.get('type')
    print(mac, typ)
    if mac is not None:        
        user.devices.append(Device(mac=mac, typ=typ))
        user.save()

    redirect('/account')

@route('/user/edit_profile')
@view('user/edit_profile')
@require_login()
def edit_profile(user):    
    return {'firstname': user.personal.firstname,
            'lastname': user.personal.lastname,
            'study_group': user.personal.study_group,
            'username': user.username}

@route('/user/edit_profile_post', method='post')
@require_login()
def edit_profile(user):
    user.personal.from_request(request)
    user.save()

    redirect('/account')
