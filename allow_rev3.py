#!/usr/bin/env python3

import sys
import re
import os
import os.path, time, datetime
import argparse
#if( len(sys.argv) < 1 ):
#	sys.stderr.write("Usage: allw.py dhcp.leases");
#	sys.exit(1)

from model import mac_status, DHCPLease, UserGroup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['iasa-wifi']
user = db.user

in_iface = 'eth1'
out_iface = 'eth0'

def load_dhcp(dhcp_lease):
    with open(dhcp_lease, "r") as fd:
        return fd.read().split("\n")

# mac_cache = dict()
# TODO
# add caching
def mac_status(mac, cur_time):
    # if mac in mac_cache and mac_cache[mac].time < 
    doc = user.find_one({"devices": {"mac": mac}}, {"group": True})
    if(doc is None):
        return ('guest', 'ACCEPT')
    elif(doc['group'] == 'blocked'):
        return ('blocked', 'DROP')
    else:
        return (doc['group'], 'ACCEPT')

def from_dhcp(st, cur_time=datetime.datetime.utcnow()):
    rules = []
    for line in st:
        line = line.strip()

        if line.startswith("lease"):
            m = re.search(r'lease\s*([0-9\.]+)\s*\{', line)
            ip = m.groups()[0]
        elif line.startswith("hardware ethernet"):
            mac = line[18:35]
        elif line.startswith("starts"):
            starts = datetime.datetime.strptime(line[7:28], "%w %Y/%m/%d %H:%M:%S")
        elif line.startswith("ends"):
            ends = datetime.datetime.strptime(line[5:26], "%w %Y/%m/%d %H:%M:%S")
        elif line.startswith("}") and ip:
            if(ends > cur_time):
                group, access = mac_status(mac, cur_time)
                rules.append((ip, mac, group, access))
            ip = None

    # rules = list(set(rules))
    return rules

def make_script(dhcp):
    # print("make_script")
    templ = [
            ('filter', "-A INPUT --src {0} -m mac --mac-source {1} -j {2}"),
            ('filter', "-A FORWARD --src {0} -m mac --mac-source {1} -j {2}"),
            ('mangle', "-A FORWARD --src {0} -j {2}"),
            ('mangle', "-A FORWARD --dst {0} -j {2}")
            ]

    iptb = {"mangle": [], "filter": []}
    i = 0
    for (ip, mac, group, access) in dhcp:
        iptb['mangle'].append("-A FORWARD --src {0} -j {2}".format(ip, mac, group))
        iptb['mangle'].append("-A FORWARD --dst {0} -j {2}".format(ip, mac, group))
        iptb['filter'].append("-A allow-inet --src {0} -m mac --mac-source {1} -j {2}".format(ip, mac, access))

    script = ''
    script += '*mangle\n'
    script += '\n'.join(iptb['mangle'])
    script += '\nCOMMIT\n'

    script += '*filter\n'
    script += ':allow-inet - [0:0]\n'
    script += '\n'.join(iptb['filter']) + '\n'

    script += 'COMMIT\n'
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


import time

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('lease_filename', type=str)
    parser.add_argument('--debug', const=True, default=False, action='store_const', help='enable debug mode')
    parser.add_argument('--profile', const=True, default=False, action='store_const', help='enable profiler mode')

    args = parser.parse_args()


    # dhcp_lease = sys.argv[1]
    # global debug
    # if(len(sys.argv) == 3 and sys.argv[2] == "debug"):
        # print("DEBUG mode")
        # debug = True

    lastmtime = 3
    while 1:
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(args.lease_filename)

        if lastmtime == mtime:
            time.sleep(1)
            # continue

        start = time.time()

        lines = load_dhcp(args.lease_filename)

        leases = from_dhcp(lines, datetime.datetime.fromtimestamp(lastmtime))
        
        
        script = make_script(leases)
        
        end = time.time()       

        if(args.debug):
            print("Loaded", len(leases), "leases")
            print("Time spend", end - start)
            print ("last modified: %s" % mtime)
        else:
            apply_script(script)
            save_dhcp(leases, lastmtime)

        # lastmtime = mtime
 
if __name__ == "__main__":
    main()
