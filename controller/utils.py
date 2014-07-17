import string
from bottle import request,redirect,response
from model import Session, UserGroup, User

def format_mac(mac):
    res = ''.join([c for c in mac.lower() if c in string.hexdigits])

    if len(res) != 12:
        return None

    mac = ':'.join([res[i:i+2] for i in range(0, len(res), 2)])
    return mac


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
    return User.objects(username=username).first() is None


def check_password(pass1, pass2):
    return len(pass1) != 0 and pass1 == pass2


def user_from_form(form):
    user = User(username=request.forms.get("username"))
    return user


def get_groups():
	groups = [g['name'] for g in UserGroup.objects]
	return groups


def start_session(user):
    session = Session(username=user['username'], user=user).save()        
    response.set_cookie('session', str(session.id))