import os, sys
import bottle

dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
os.chdir(dir)
sys.path.insert(0, dir)

from controller import login, admin, user
application = bottle.default_app()
#from main import *
