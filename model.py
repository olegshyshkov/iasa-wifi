#!/usr/bin/python3

from mongoengine import *

connect("iasa-wifi")

class Device(EmbeddedDocument):
    mac = StringField()

class PresonalInfo(EmbeddedDocument):
    firstname = StringField()
    lastname = StringField()
    study_group = StringField()
    email = StringField()


class User(Document):
    username = StringField(primary_key=True)
    password = StringField()
    access = BooleanField()
    fake = BooleanField()    
    devices = ListField(EmbeddedDocumentField(Device))
    personal = EmbeddedDocumentField(PresonalInfo)
    verified = ListField(EmbeddedDocumentField(PresonalInfo))
    group = StringField()


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
