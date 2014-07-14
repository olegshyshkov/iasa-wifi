import string
from bcrypt import hashpw
from bottle import request
from model import Session, UserGroup, User

def format_mac(mac):
    res = ''.join([c for c in mac.lower() if c in string.hexdigits])

    if len(res) != 12:
        return None

    mac = ':'.join([res[i:i+2] for i in range(0, len(res), 2)])
    return mac


def is_good_password(hashpass, raw_pass):
    return hashpw(raw_pass, hashpass) == hashpass


def require_login(roles_require=None):
    def decorator(f):
        def access_denied(*args, **kwargs):
            return "Access denied"

        def tmp(*args, **kwargs):
            cookie = request.get_cookie("session")
            if cookie is None:
                redirect("/login")

            session = Session.objects(id=cookie).first()

            if session is None:
                redirect("/login")

            user = session.user
            if user is None:
                redirect("/login")

            if roles_require is not None:
                if user['group'].name not in roles_require:
                    return "Access denied"

            return f(user, *args, **kwargs)
        return tmp
    return decorator

def check_login(username):
    print("check_login: '" + username + "'")
    return username != ''

def check_password(pass1, pass2):
    return len(pass1) != 0 and pass1 == pass2

def user_from_form(form):
    user = User(username=request.forms.get("username"))
    return user
    #return {k: request.forms.get(k) for k in request.forms}

def get_groups():
	groups = [g['name'] for g in UserGroup.objects]
	return groups