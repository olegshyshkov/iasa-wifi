import unittest

from allow_rev3 import from_dhcp, make_script

import datetime
from model import DHCPLease

class TestDHCP(unittest.TestCase):
	def test_sum(self):
		a = 10
		b = 15
		c = 25
		self.assertEqual(a + b, c)

	def test_from_dhcp_one_lease(self):
		text = """
		lease 192.168.189.142 {
		  starts 1 2014/06/09 11:42:11;
		  ends 2 2014/06/10 11:40:32;
		  tstp 2 2014/06/10 11:40:32;
		  cltt 1 2014/06/09 11:42:11;
		  binding state free;
		  hardware ethernet 48:5a:3f:32:08:36;
		  uid "\001HZ?2\0106";
		}
		""".split("\n")

		cur_time = datetime.datetime(2014, 6, 10, 0, 0, 1)
		st = from_dhcp(text, cur_time)

		(ip, mac, group, access) = st[0]

		self.assertEqual(mac, "48:5a:3f:32:08:36")
		self.assertEqual(ip, "192.168.189.142")
		# self.assertEqual(st[0].ends, datetime.datetime(2014, 6, 10, 11, 40, 32))
		# self.assertEqual(st[0].starts, datetime.datetime(2014, 6, 9, 11, 42, 11))

	def test_make_script(self):
		lease = ("192.168.189.142", "48:5a:3f:32:08:36",
			"guest",
			"ACCEPT")

		script = make_script([lease])

		res = \
"""*mangle
-A FORWARD --src 192.168.189.142 -j guest
-A FORWARD --dst 192.168.189.142 -j guest
COMMIT
*filter
:allow-inet - [0:0]
-A allow-inet --src 192.168.189.142 -m mac --mac-source 48:5a:3f:32:08:36 -j ACCEPT
COMMIT
"""
	
		self.assertEqual(res, script)


if __name__ == '__main__':
	unittest.main()