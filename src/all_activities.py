#!/usr/bin/env python
# -*- coding: utf-8 -*-


__version__ = '0.01'
__copyright__ = 'Copyright © 2013'


try:
	settings = __import__('settings')
except ImportError:
	print 'Error import module "settings", see settings.py.template'
	sys.exit(1)
IS_KEY = getattr(settings, 'IS_KEY')
IMG_CACHE = getattr(settings, 'IMG_CACHE', {})
import os.path
import datetime, pytz
from libkanojo import ActivityBlock, Kanojo


domain='www.barcodekanojo.com'
server='http://%s'%domain


if __name__=='__main__':
	script_path = os.path.dirname(os.path.realpath(__file__))

	dt = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
	last_msg_hash = None
	hash_file = script_path+'/last_msg_hash'
	if os.path.isfile(hash_file):
		last_msg_hash = open(hash_file).read()

	kanojo = Kanojo(last_msg_hash)
	kanojo.IS_KEY = IS_KEY;
	kanojo.IMG_CACHE = IMG_CACHE
	html_data = kanojo.get_htmldata(server)
	#html_data = open('index.html').read()

	if not isinstance(html_data, int):
		msgs = kanojo.parse_data(html_data)
		print len(msgs)
		if len(msgs):
			fn = '/'.join(script_path.split('/')[:-1])+'/%s.md'%dt.strftime('%Y_%m_%d')

			f = open(fn, 'a')
			for ab in msgs:
				if ab.time:
					tm = dt - datetime.timedelta(0, ab.time)
					print ab.hash(), tm.strftime('%H:%M'), ab.c_box_text
				str = ''
				if ab.l_box_url != None:
					f.write('[![img](%s)](%s) '%(ab.l_box_image, ab.l_box_url))
				if ab.time:
					tm = dt - datetime.timedelta(0, ab.time)
					f.write(tm.strftime('%H:%M '))
				f.write(ab.c_box_text)
				if ab.r_box_url != None:
					f.write('[![img](%s)](%s) '%(ab.r_box_image, ab.r_box_url))
				f.write('\n\n')
			f.close()

			f = open(hash_file, 'w')
			f.write(msgs[-1].hash())
			f.close()
