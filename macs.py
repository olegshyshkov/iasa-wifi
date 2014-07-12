#!/usr/bin/python3

from mongoengine import *

connect('macs')

class Mac(Document):
	mac = StringField(unique = True)
	access = BooleanField(default = True)


if __name__ == "__main__":
	m = Mac(mac = '11:22:33:44:55:66')
	try:
		m.save()
	except:
		pass


	m = Mac.objects()
	print(len(m))
