#!/usr/bin/env python2

import re
import os
import os.path
import time
from datetime import datetime as dt
import argparse

from collections import namedtuple
# from model import DHCPLease
# from model import UserGroup

from pymongo import MongoClient

import xxhash

in_iface = 'eth1'
out_iface = 'eth0'

MacCache = namedtuple('MacCache', ['val', 'time'])


class DHCP:
    def __init__(self, user):
        self.CACHE_TIME = 7
        self.user = user
        self.mac_cache = dict()

        self.dhcp_cache = []
        self.dhcp_cache_len = 0
        self.dhcp_hash = ""

    def load_dhcp(self, dhcp_lease):
        with open(dhcp_lease, "r") as fd:
            return fd.read().split("\n")

    def mac_status(self, mac, cur_time=None):
        if cur_time is None:
            cur_time = dt.utcnow()

        life_time = (cur_time - self.mac_cache[mac].time).total_seconds()
        if mac in self.mac_cache and life_time < self.CACHE_TIME:
            return self.mac_cache[mac].val
        else:
            doc = self.user.find_one({"devices": {"mac": mac}}, {"group": True})
            # doc = None
            if doc is None:
                res = ('guest', 'ACCEPT')
            elif doc['group'] == 'blocked':
                res = ('blocked', 'DROP')
            else:
                res = (doc['group'], 'ACCEPT')
            self.mac_cache[mac] = MacCache(res, cur_time)
            return res

    def cached_parse_dhcp(self, lines, cur_time=None):
        if cur_time is None:
            cur_time = dt.utcnow()
        m = xxhash.xxh64()
        m.update("".join(lines[:self.dhcp_cache_len]).encode("utf8"))
        new_hash = m.digest()
        # new_len = len(lines)

        if new_hash != self.dhcp_hash:
            self.dhcp_cache_len = 0
            self.dhcp_cache = []
            m = xxhash.xxh64()

        lines = lines[self.dhcp_cache_len:]
        self.dhcp_cache.extend(self.from_dhcp(lines, cur_time))
        m.update("".join(lines).encode("utf8"))
        self.dhcp_hash = m.digest()
        self.dhcp_cache_len += len(lines)

        return self.dhcp_cache

    def from_dhcp(self, st, cur_time=None):
        if cur_time is None:
            cur_time = dt.utcnow()

        rules = []
        for line in st:
            line = line.strip()

            if line.startswith("lease"):
                m = re.search(r'lease\s*([0-9\.]+)\s*\{', line)
                ip = m.groups()[0]
            elif line.startswith("hardware ethernet"):
                mac = line[18:35]
            elif line.startswith("starts"):
                starts = dt.strptime(line[7:28], "%w %Y/%m/%d %H:%M:%S")
            elif line.startswith("ends"):
                ends = dt.strptime(line[5:26], "%w %Y/%m/%d %H:%M:%S")
            elif line.startswith("}") and ip:
                if(ends > cur_time):
                    group, access = self.mac_status(mac, cur_time)
                    # rules.append((ip, mac, group, access))
                    rules.append((ip, mac, starts, ends))
                ip = None

        rules = list(set(rules))

        return rules

    def make_script(self, dhcp):
        # print("make_script")
        # templ = [
        # ('filter', "-A INPUT --src {0} -m mac --mac-source {1} -j {2}"),
        # ('filter', "-A FORWARD --src {0} -m mac --mac-source {1} -j {2}"),
        # ('mangle', "-A FORWARD --src {0} -j {2}"),
        # ('mangle', "-A FORWARD --dst {0} -j {2}")
        #                ]
        iptb = {"mangle": [], "filter": []}

        filter_tmpl = "-A allow-inet --src {0} -m mac --mac-source {1} -j {2}"
        for (ip, mac, group, access) in dhcp:
            iptb['mangle'].append(
                "-A FORWARD --src {0} -j {2}".format(ip, mac, group))
            iptb['mangle'].append(
                "-A FORWARD --dst {0} -j {2}".format(ip, mac, group))
            iptb['filter'].append(filter_tmpl.format(ip, mac, access))

        script = ''
        script += '*mangle\n'
        script += '\n'.join(iptb['mangle'])
        script += '\nCOMMIT\n'

        script += '*filter\n'
        script += ':allow-inet - [0:0]\n'
        script += '\n'.join(iptb['filter']) + '\n'

        script += 'COMMIT\n'
        return script

    def apply_script(self, script):
        # print("apply_script")
        fd = os.popen("sudo iptables-restore --noflush", "w")
        fd.write(script)
        fd.close()

    def save_dhcp(self, dhcp, last):
        # print("save_dhcp")
        last = dt.utcfromtimestamp(last - 3)
        # print("Last: ", last)
        for lease in dhcp:
            # print(lease.starts, last)
            if(lease.starts >= last):
                # print("save")
                lease.save()


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('lease_filename', type=str)
    parser.add_argument('--debug', const=True, default=False,
                        action='store_const', help='enable debug mode')
    parser.add_argument('--profile', const=True, default=False,
                        action='store_const', help='enable profiler mode')

    args = parser.parse_args()

    client = MongoClient('localhost', 27017)
    db = client['iasa-wifi']
    user = db.user
    dhcp = DHCP(user)

    lastmtime = 0
    while 1:
        mtime = os.stat(args.lease_filename)[-2]

        if lastmtime == mtime:
            time.sleep(1)
            continue

        start = time.time()

        lines = dhcp.load_dhcp(args.lease_filename)
        leases = dhcp.cached_parse_dhcp(lines, dt.fromtimestamp(lastmtime))
        script = dhcp.make_script(leases)

        end = time.time()

        if(args.debug):
            print("Loaded", len(leases), "leases")
            print("Time spend", end - start)
            print ("last modified: %s" % mtime)
        else:
            dhcp.apply_script(script)
            dhcp.save_dhcp(leases, lastmtime)

        lastmtime = mtime

if __name__ == "__main__":
    main()
