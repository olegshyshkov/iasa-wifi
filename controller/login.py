__author__ = 'olage'

from bottle import route, view, run
from bottle import request, response, redirect
from bcrypt import hashpw, gensalt

from model import Session, User
from .utils import *


@route('/')
def root():
    redirect('/login')

@route('/login')
@view('login')
def login(err=''):
    return {'err': err}


@route('/login', method='POST')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')

    user = User.objects(username=username).first()

#    print(user['username'], user['password'], hashpw(password.encode('utf-8'), user['password'])) # .encode('utf-8')))
    print(user['username'], user['password'], hashpw(password.encode('utf-8'), user.password)) # .encode('utf-8')))

    if is_good_password(user['password'], password.encode('utf-8')):
        session = Session(username=user['username'], user=user).save()        
        response.set_cookie('session', str(session.id))
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