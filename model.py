#!/usr/bin/python3

from bcrypt import hashpw
from mongoengine import *

connect("iasa-wifi")

class Device(EmbeddedDocument):
    mac = StringField()
    typ = StringField()

class PersonalInfo(EmbeddedDocument):
    firstname = StringField(default="")
    lastname = StringField(default="")
    study_group = StringField(default="")
    email = StringField(default="")

    def from_request(self, request):
        self.firstname = request.forms.get('firstname')
        self.lastname = request.forms.get('lastname')
        self.study_group = request.forms.get('study_group')

class UserGroup(Document):
    name = StringField(primary_key=True)
    access = BooleanField(default=True)

#unv = UserGroup(id=b"0", name="unverified").save()
#UserGroup(id=b"1", name="verified").save()
#UserGroup(id=b"2", name="admin").save()


unv = UserGroup(name="unverified").save()
UserGroup(name="verified").save()
admin = UserGroup(name="admin").save()
UserGroup(name="blocked", access=False).save()

class User(Document):
    username = StringField(primary_key=True)
    password = BinaryField()
    fake = BooleanField()
    devices = ListField(EmbeddedDocumentField(Device))
    personal = EmbeddedDocumentField(PersonalInfo, default=PersonalInfo())
    verified = ListField(EmbeddedDocumentField(PersonalInfo))
    group = ReferenceField(UserGroup, default=unv)

    def is_good_password(self, password):
        if type(password) is str:
            password = password.encode("utf-8")
        return hashpw(password, self.password) == self.password


class Session(Document):
    user = ReferenceField(User)
    username = StringField()

class DHCPLease(Document):
    ip = StringField()
    mac = StringField()
    starts = DateTimeField()
    ends =  DateTimeField()

#user = User(username="blage", devices=[ Device(mac="111")]).save()
#print(User.objects(devices=Device(mac="111")))
#print(user.username)

def mac_status(mac):
    user = User.objects(devices=Device(mac=mac)).first()

    # TODO: DELETE IN RELEASE
    if user is None:
        user = User.objects(username="dummy").first()  
        user.devices.append(Device(mac=mac))
        user.save()
    
    if user.group.access:
        return "ACCEPT"
    else:
        return "DROP"

try:
    User(username="dummy", access=True, devices=[ ]).save(force_insert=True)
except:
    pass

try:
    User(username="admin", group=admin, 
        password=b'$2a$10$CV02h8R7BJSyanE3Tmb88Ojb3CrI.l6vHfckrfWOR208Gcm1q9hn.').save(force_insert=True)
except:
    pass
