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

            if(ends > now or debug):
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

def make_script(dhcp):
    templ = [
             ('filter', "-A INPUT --src {0} -m mac --mac-source {1} -j {2}"),
             ('filter', "-A FORWARD --src {0} -m mac --mac-source {1} -j {2}"),
             ('mangle', "-A FORWARD --src {0} -j {2}"),
             ('mangle', "-A FORWARD --dst {0} -j {2}")
            ]

    iptb = {"mangle": [], "filter": []}

    for lease in dhcp:
        jump = mac_status(lease.mac)
        print(lease.mac, jump, jump.name, jump.access)        
        #for (table, rule) in templ:
        #    iptb[table].append(rule.format(ip, mac, jump))
            
            
        iptb['mangle'] += ["-A FORWARD --src {0} -j {2}".format(lease.ip, lease.mac, jump.name)]
        iptb['mangle'] += ["-A FORWARD --dst {0} -j {2}".format(lease.ip, lease.mac, jump.name)]
        iptb['filter'] += ["-A allow_inet --src {0} -m mac --mac-source {1} -j {2}".format(lease.ip, lease.mac, jump.access)]
        #iptb['filter'] += ["-A INPUT --src {0} -m mac --mac-source {1} -j {2}".format(ip, mac, jump.access)]
        #iptb['filter'] += ["-A FORWARD --src {0} -m mac --mac-source {1} -j {2}".format(ip, mac, jump.access)]

    script = ''
    script += '*mangle\n'

#    for o in UserGroup.objects:
 #       script += o.to_iptables()

    script += '\n'.join(iptb['mangle'])
    script += '\nCOMMIT\n'


    script += '*filter\n'
    script += ':allow_inet - [0:0]\n'
    #script += '-F allow_inet\n'.format(in_iface)
    script += '\n'.join(iptb['filter']) + '\n'
    #script += '-A FORWARD -j allow_inet\n'
    #script += '-A INPUT -j allow_inet\n'
    script += '-A allow_inet -i {0} -j DROP\n'.format(in_iface)
    
    script += 'COMMIT\n'

    return script

def apply_script(script):
    fd = os.popen("sudo iptables-restore --noflush", "w")
    fd.write(script)
    fd.close()

def prepare_iptables():
    script = []
    script += ['FORWARD -j allow_inet']
    script += ['INPUT -j allow_inet']
    
    script = ''.join(
        ['sudo iptables -D ' + s + '\n' for s in script] + 
        ['sudo iptables -A ' + s + '\n' for s in script]
        )

    for o in UserGroup.objects:
        script += o.to_iptables()

    print(script)
    os.system(script)


def prepare_tc():
    script =  """sudo tc qdisc del dev {0} root\nsudo tc qdisc add dev {0} root handle 1: htb\n"""
    for o in UserGroup.objects:
        script += o.to_tc()

  #  print(script)
    os.system(script.format(in_iface))
    os.system(script.format(out_iface))
    

def save_dhcp(dhcp, last):
    last = datetime.datetime.utcfromtimestamp(last - 3)
    #print("Last: ", last)
    for lease in dhcp:
        print(lease.starts, last)
        if(lease.starts >= last):
            print("save")
            lease.save()

def main():
    dhcp_lease = sys.argv[1]
    global debug
    if(len(sys.argv) == 3 and sys.argv[2] == "debug"):
        print("DEBUG mode")
        debug = True

    prepare_tc()
    prepare_iptables()
   # return;
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

if __name__ == "__main__":
    main()
