#!/usr/bin/env python3

import sys
import re
import os
import os.path, time, datetime
#if( len(sys.argv) < 1 ):
#	sys.stderr.write("Usage: allw.py dhcp.leases");
#	sys.exit(1)

from model import mac_status, DHCPLease

debug = False

class IpTablesRule:
    def __init__(self, *kargs):
        if(len(kargs) == 1):
            lst = kargs[0]
            self.chain = lst[1]
            self.ip = lst[3][:-3] if lst[3].endswith("/32") else lst[3]            
            self.mac = lst[9]
            self.jump = lst[11]
            self.iface = lst[5]
        else:
            self.ip = kargs[0]
            self.mac = kargs[1]
            self.jump = kargs[2]
            self.chain = kargs[3]
            self.iface = kargs[4]
            self.starts = kargs[5]
            self.ends = kargs[6]
        self.mac = self.mac.upper()
        
    def __str__(self):
        return "{} -s {}/32 -i {} -m mac --mac-source {} -j {}\n".format(self.chain, self.ip, self.iface, self.mac, self.jump)
    
    def to_add(self):
        return "sudo iptables -A " + str(self)  
    
    def to_delete(self):
        return "sudo iptables -D " + str(self)
    
    def __eq__(self, other):
        return self.ip == other.ip and self.mac.upper() == other.mac.upper() and self.jump == other.jump
            
    def __ne__(self, other):
        return not (self == other)
    
    def __hash__(self):
        return hash(str(self))
   
    def save_to_mongo(self):
        DHCPLease(ip=self.ip, mac=self.mac, starts=self.starts, ends=self.ends).save()

class IpTablesParser:
    def __init__(self, dhcp_lease, chain_name, iface_name):        
        self.dhcp_lease = dhcp_lease
        self.chain_name = chain_name
        self.iface_name = iface_name
    
    def from_dhcp(self):
        with open(self.dhcp_lease, "r") as fd:
            st = fd.read().split("\n")
        
        ends = ''
        starts = ''
        mac = ''

        macs = dict()
        jump = "ACCEPT"
        rules = []
        for line in st:
            if not line or line.startswith("#"):
                continue;

            if line == '}' and lease:
                now = datetime.datetime.utcnow()               

                if(ends > now or debug):
                    macs[lease] = mac
                    rules.append(IpTablesRule(lease, mac, mac_status(mac), self.chain_name, self.iface_name, starts, ends))

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
    
    def from_iptables(self):
        with os.popen("sudo iptables-save") as fd:
            return [IpTablesRule(s.split()) for s in fd if len(s.split()) == 12 and s.startswith("-A " + self.chain_name)] 
  
class IpTables():
    def __init__(self, dhcp, chain, iface):
        self.chain = chain
        self.parser = IpTablesParser(dhcp, chain, iface)
        script = """sudo iptables -F {0}
                    sudo iptables -N {0}
                    sudo iptables -D FORWARD -j {0}
                    sudo iptables -A FORWARD -j {0}
                    sudo iptables -D POSTROUTING -t nat -o eth0 -j MASQUERADE
                    sudo iptables -A POSTROUTING -t nat -o eth0 -j MASQUERADE
                     """.format(self.chain)
        print(script)
        os.system( script )


    def update_old_style(self):
        rules = self.parser.from_dhcp()
        
        script = """sudo iptables -F {0}\n""".format(self.chain)
        for r in rules:
            script += "sudo iptables -A {} -i eth1 -s {} -m mac --mac-source {} -j {}\n".format(self.chain, r.ip, r.mac, r.jump)
        script += "sudo iptables -A {} -i eth1 -j DROP\n".format(self.chain)
        return script
    
    def update(self):        
        old_rules = set(self.parser.from_iptables())
        new_rules = set(self.parser.from_dhcp())

        script = ""
        script += "sudo iptables -D {} -j DROP\n".format(self.chain)

        for r in old_rules - new_rules:
            script += r.to_delete()

        for r in new_rules - old_rules:
            script += r.to_add()
            r.save_to_mongo()
        
        script += "sudo iptables -A {} -j DROP\n".format(self.chain)
        return script


def main():
    lastmtime = None

    dhcp_lease = sys.argv[1]
    global debug
    if(len(sys.argv) == 3 and sys.argv[2] == "debug"):
        print("DEBUG mode")
        debug = True

    ip = IpTables(dhcp_lease, "allow_inet", "eth1")

    while 1:
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dhcp_lease)

        if lastmtime == None:
            lastmtime = mtime
        elif lastmtime == mtime:
            time.sleep(1)
            continue

        lastmtime = mtime

        print ("last modified: %s" % mtime)
        script = ip.update()
        if(debug):
            print(script)
        os.system( script )

#		sys.exit()

if __name__ == "__main__":
    main()
