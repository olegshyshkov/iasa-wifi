#!/usr/bin/python3

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

#unv = UserGroup(id=b"0", name="unverified").save()
#UserGroup(id=b"1", name="verified").save()
#UserGroup(id=b"2", name="admin").save()


unv = UserGroup(name="unverified").save()
UserGroup(name="verified").save()
UserGroup(name="admin").save()

class User(Document):
    username = StringField(primary_key=True)
    password = BinaryField()
    access = BooleanField()
    fake = BooleanField()    
    devices = ListField(EmbeddedDocumentField(Device))
    personal = EmbeddedDocumentField(PersonalInfo, default=PersonalInfo())
    verified = ListField(EmbeddedDocumentField(PersonalInfo))
    group = ReferenceField(UserGroup, default=unv)

class Session(Document):
    user = ReferenceField(User)
    username = StringField()


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
    
    if user.access:
        return "ACCEPT"
    else:
        return "DROP"


user = User(username="dummy", access=True, devices=[ ]).save()


#print(mac_status("111"))
