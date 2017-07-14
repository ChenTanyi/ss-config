#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
import base64
import qrtools
import urllib2

#------------ input ----------------
os.chdir('/home/c-tan-one/software/shadowsock/')
file_name = 'ss.json'

#------------ function -------------

def decodeUrl(url):
	raw = base64.b64decode(url[5:]).strip().split(':')
	assert(len(raw) == 3)
	return [raw[0]] + raw[1].split('@') + [int(raw[2])]

if __name__ == '__main__':

	with open(file_name, 'r') as f:
		config = json.load(f)

	print json.dumps(config, indent = 2)

	if len(sys.argv) < 2:
		return

	if len(sys.argv) == 2:	
		config['password'] = sys.argv[1]
	elif sys.argv[1] == '-u' or sys.argv[1] == '--url':
		config['method'], config['password'], config['server'], config['server_port'] = decodeUrl(sys.argv[2])
	elif sys.argv[1] == '-i' or sys.argv[1] == '--image':
		url = sys.argv[2]
		qrImgFile = url.split('/')[-1]

		try:
			u = urllib2.urlopen(url)
			with open(qrImgFile, 'wb') as qrImg:
				qrImg.write(u.read())
		except:
			if os.path.exists(qrImgFile):
				os.remove(qrImgFile)
			print >> sys.stderr, 'Can read the image of ' + url
			exit(1)

		qr = qrtools.QR()
		qr.decode(qrImgFile)
		config['method'], config['password'], config['server'], config['server_port'] = decodeUrl(qr.data)

		os.remove(qrImgFile)
	else:
		for i, item in enumerate(config):
			if i + 1 < len(sys.argv):
				if item != 'password':
					try:
						config[item] = int(sys.argv[i + 1])
					except:
						config[item] = sys.argv[i + 1]
				else:
					config[item] = sys.argv[i + 1]
			else:
				break

	print json.dumps(config, indent = 2)

	with open(file_name, 'w') as f:
		json.dump(config, f, indent = 2)