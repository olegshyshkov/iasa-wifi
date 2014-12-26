#!/usr/bin/env python3

import sys
import re
import os
import os.path, time, datetime
#if( len(sys.argv) < 1 ):
#	sys.stderr.write("Usage: allw.py dhcp.leases");
#	sys.exit(1)

from model import mac_status, DHCPLease, UserGroup

in_iface = 'eth1'
out_iface = 'eth0'

debug = False

def from_dhcp(dhcp_lease):
    with open(dhcp_lease, "r") as fd:
        st = fd.read().split("\n")
    
    ends = ''
    starts = ''
    mac = ''

    rules = []
    for line in st:
        if not line or line.startswith("#"):
            continue;

        if line == '}' and lease:
            now = datetime.datetime.utcnow()               

            if(ends > now): # or debug):
                rules.append(DHCPLease(ip=lease, mac=mac, starts=starts, ends=ends))

            lease = None
            continue

        m = re.search(r'lease\s*([0-9\.]+)\s*\{', line)
        if m:
            lease = m.groups()[0]
            continue

        m = re.search(r'\s+([a-z\s\-]+)\s+\"?(.+?)?\"?\;', line)
        if m:
            k, v = m.groups()
            if k == "hardware ethernet":
                mac = v
            elif k == "ends":
                ends = datetime.datetime.strptime(v, "%w %Y/%m/%d %H:%M:%S")
            elif k == "starts":
                starts = datetime.datetime.strptime(v, "%w %Y/%m/%d %H:%M:%S")


    return rules


from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['iasa-wifi']
user = db.user

class Group():
    def __init__(self, name):
        self.name = name
        self.access = "ACCEPT"

def mac_status(doc):
    if(doc == None):
        jump = Group('guest')
    else:
        jump = Group(doc['group'])
    return jump

def make_script(dhcp):
    print("make_script")
    templ = [
            ('filter', "-A INPUT --src {0} -m mac --mac-source {1} -j {2}"),
            ('filter', "-A FORWARD --src {0} -m mac --mac-source {1} -j {2}"),
            ('mangle', "-A FORWARD --src {0} -j {2}"),
            ('mangle', "-A FORWARD --dst {0} -j {2}")
            ]

    iptb = {"mangle": [], "filter": []}
    i = 0
    for lease in dhcp:
        doc = user.find_one({"devices": {"mac": lease.mac}})

        jump = mac_status(doc)
#        print(lease.mac, jump, jump.name, jump.access)

        iptb['mangle'] += ["-A FORWARD --src {0} -j {2}".format(lease.ip, lease.mac, jump.name)]
        iptb['mangle'] += ["-A FORWARD --dst {0} -j {2}".format(lease.ip, lease.mac, jump.name)]
        iptb['filter'] += ["-A allow-inet --src {0} -m mac --mac-source {1} -j {2}".format(lease.ip, lease.mac, jump.access)]

    script = ''
    script += '*mangle\n'
    script += '-F FORWARD\n'
    script += '\n'.join(list(set(iptb['mangle'])))
    script += '\nCOMMIT\n'

    script += '*filter\n'
    script += ':allow-inet - [0:0]\n'
    script += '\n'.join(list(set(iptb['filter']))) + '\n'

    script += 'COMMIT\n'
#    print(script)
    return script

def apply_script(script):
    print("apply_script")
    fd = os.popen("sudo iptables-restore --noflush", "w")
    fd.write(script)
    fd.close()

def save_dhcp(dhcp, last):
    print("save_dhcp")
    last = datetime.datetime.utcfromtimestamp(last - 3)    
    #print("Last: ", last)
    for lease in dhcp:
        #print(lease.starts, last)
        if(lease.starts >= last):
            #print("save")
            lease.save()

def main():
    dhcp_lease = sys.argv[1]
    global debug
    if(len(sys.argv) == 3 and sys.argv[2] == "debug"):
        print("DEBUG mode")
        debug = True

    lastmtime = 3
    while 1:
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dhcp_lease)

        if lastmtime == mtime:
            time.sleep(1)
            continue

        dhcp = from_dhcp(dhcp_lease)
        save_dhcp(dhcp, lastmtime)

        script = make_script(dhcp)

        if(debug):
            print(script)
        apply_script(script)       

        lastmtime = mtime

        print ("last modified: %s" % mtime)
        #return
if __name__ == "__main__":
    main()
