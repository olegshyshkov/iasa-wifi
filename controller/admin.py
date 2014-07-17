__author__ = 'olage'

from bottle import run, route, view, redirect
from bottle import template, request

from model import Session, PersonalInfo, User, UserGroup
from .utils import *

@route('/administration')
@view('admin/administration')
@require_login(roles_require=["admin"])
def administration(user):
    users_list = User.objects
    return {'users': users_list}


@route('/user/<username>')
@view('admin/verify_user')
@require_login(roles_require=["admin"])
def verified_user(user, username):
    user = User.objects(username=username).first()
    groups = get_groups()
    group = user.group

    if len(user.verified) == 0:
        verified = PersonalInfo()
    else:
        verified = user.verified[-1]

    params = [(k, user.personal[k], verified[k]) for k in verified]

    return {'username': username,
            'params': params,
            'group': group.name,
            'groups': groups}


@route('/user/<username>', method='post')
@require_login(roles_require=["admin"])
def verified_user_verify(user, username):
    user = User.objects(username=username).first()
    user.verified.append(user.personal)
    user.save()
    #return verified_user(username)
    redirect('/user/' + username)


@route('/block_user', method='post')
@require_login(roles_require=["admin"])
def block_user(user):
    username = request.forms.get('username')
    access = eval(request.forms.get('access'))
    user = User.objects(username=username).first()
    user.access = not access
    user.save()
    redirect('/administration')

@route('/user/change_group', method='post')
@require_login(roles_require=["admin"])
def change_group(user):
    username = request.forms.get('username')
    user = User.objects(username=username).first()
    group = request.forms.get('group')
    user['group'] = UserGroup(name=group)
    user.save()
    redirect("/user/" + username)