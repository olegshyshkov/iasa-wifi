#!/usr/bin/python3

from bcrypt import hashpw, gensalt
from mongoengine import *

connect("iasa-wifi")

class Device(EmbeddedDocument):
    mac = StringField()
    typ = StringField()

class PersonalInfo(EmbeddedDocument):
    first_name = StringField(default="")
    last_name = StringField(default="")
    middle_name = StringField(default="")
    study_group = StringField(default="")
    email = StringField(default="")
    skype = StringField(default="")
    icq = StringField(default="")
    phone_number = StringField(default="")

    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.middle_name = data['middle_name']
        self.study_group = data['study_group']
        self.email = data['email']
        self.skype = data['skype']
        self.icq = data['icq']
        self.phone_number = data['phone_number']

class UserGroup(Document):
    name = StringField(primary_key=True)
    access = StringField(default='ACCEPT')
    mark = IntField()
    rate = StringField(default="54kbps")

    def to_iptables(self):
       # s = ':{0.name} - [0:0]\n'
        script = ['-N {0.name} -t mangle']
        script += ['-t mangle -D {0.name} -j MARK --set-mark {0.mark}']
        script += ['-t mangle -A {0.name} -j MARK --set-mark {0.mark}']
        return [s.format(self) for s in script]

    def to_tc(self):
        s = """sudo tc class add dev {0} parent 1: classid 1:{1.mark} htb rate {1.rate}
sudo tc filter add dev {0} parent 1:0 prio 1 protocol ip handle {1.mark} fw flowid 1:{1.mark}
"""
        return s.format("{0}", self)


#unv = UserGroup(id=b"0", name="unverified").save()
#UserGroup(id=b"1", name="verified").save()
#UserGroup(id=b"2", name="admin").save()


guest = UserGroup(name="guest", mark=0x10).save()
unv   = UserGroup(name="unverified", mark=0x20).save()
UserGroup(name="verified", mark=0x30).save()
admin = UserGroup(name="admin", mark=0x40, rate="1mbps").save()
UserGroup(name="blocked", access='DROP', mark=0x50).save()

class User(Document):
    username = StringField(primary_key=True)
    password = BinaryField()
    fake = BooleanField()
    admin = BooleanField(default=False)
    devices = ListField(EmbeddedDocumentField(Device))
    personal = EmbeddedDocumentField(PersonalInfo, default=PersonalInfo())
    verified = ListField(EmbeddedDocumentField(PersonalInfo))
    group = ReferenceField(UserGroup, default=unv)
    vk_id = StringField(default="")
    fb_id = StringField(default="")
    g_id = StringField(default="")    

    def is_good_password(self, password):
        if type(password) is str:
            password = password.encode("utf-8")
        return hashpw(password, self.password) == self.password


    def from_dict(self, data):
        self.username = data['username']
        pass1 = data['password1']
        self.password = hashpw(pass1.encode('utf-8'), gensalt(10))
        uid = data['uid'].split(":", 1)
        if uid[0] == 'vk':
            self.vk_id = uid[1]
        elif uid[0] == 'fb':
            self.fb_id = uid[1]
        elif uid[0] == 'g':
            self.g_id = uid[1]
        self.personal.from_dict(data)


class DHCPLease(Document):
    ip = StringField()
    mac = StringField()
    starts = DateTimeField()
    ends =  DateTimeField()

def mac_status(mac):
    user = User.objects(devices__mac=mac).first()
    if user is None:
        return guest
    else:
        return user.group


try:
    User(username="admin", group=admin, 
        password=b'$2a$10$7TbBBEtcV01.1OLQo96xROnyy2dP4/xey.hl0RC8sGawH5Iaj1OSS').save(force_insert=True)
except:
    pass
