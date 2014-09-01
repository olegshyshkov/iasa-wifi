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

    def from_request(self, request):
        self.first_name = request.forms.get('first_name')
        self.last_name = request.forms.get('last_name')
        self.middle_name = request.forms.get('middle_name')
        self.study_group = request.forms.get('study_group')
        self.email = request.forms.get('email')
        self.skype = request.forms.get('skype')
        self.icq = request.forms.get('icq')
        self.phone_number = request.forms.get('phone_number')

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
    vk_id = StringField()
    fb_id = StringField()
    g_id = StringField()

    def is_good_password(self, password):
        if type(password) is str:
            password = password.encode("utf-8")
        return hashpw(password, self.password) == self.password

    def from_request(self, request):
        self.username = request.forms.get('username')
        pass1 = request.forms.get('pass1')
        self.password = hashpw(pass1.encode('utf-8'), gensalt(10))
        uid = request.forms.get('uid').split(":", 1)
        if uid[0] == 'vk':
            self.vk_id = uid[1]
        elif uid[0] == 'fb':
            self.fb_id = uid[1]
        elif uid[0] == 'g':
            self.g_id = uid[1]
        self.personal.from_request(request)



class Session(Document):
    session_id = StringField()
    user = ReferenceField(User)
    username = StringField()

class DHCPLease(Document):
    ip = StringField()
    mac = StringField()
    starts = DateTimeField()
    ends =  DateTimeField()

    #def __init__(self, ip, mac, starts, ends):
    #    super(Document, self)
        #self.ip = ip
        #self.mac = mac
        #self.starts = starts
        #self.ends = ends


#user = User(username="blage", devices=[ Device(mac="111")]).save()
#print(User.objects(devices=Device(mac="111")))
#print(user.username)

def mac_status(mac):
#    return guest
    user = User.objects(devices__mac=mac).first()
    #print(mac, user)
    if user is None:
        return guest
    else:
        return user.group


try:
    User(username="admin", group=admin, 
        password=b'$2a$10$7TbBBEtcV01.1OLQo96xROnyy2dP4/xey.hl0RC8sGawH5Iaj1OSS').save(force_insert=True)
except:
    pass
