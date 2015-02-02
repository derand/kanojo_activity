#!/usr/bin/env python
# -*- coding: utf-8 -*-


__version__ = '0.01'
__copyright__ = 'Copyright © 2013'


try:
	settings = __import__('settings')
except ImportError:
	print 'Error import module "settings", see settings.py.template'
	exit(1)
IS_KEY = getattr(settings, 'IS_KEY')
IMG_CACHE = getattr(settings, 'IMG_CACHE', {})
WRITE_LOG = getattr(settings, 'WRITE_LOG', False)
import datetime, pytz
from libkanojo import ActivityBlock, Kanojo
import json
import os
from time import localtime, strftime, time
import random

domain='www.barcodekanojo.com'
server='http://%s'%domain


if __name__=='__main__':
	start_time = time()

	script_path = os.path.dirname(os.path.realpath(__file__))

	dt = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
	last_msg_hash = None
	hash_file = script_path+'/last_msg_hash'
	if os.path.isfile(hash_file):
		last_msg_hash = open(hash_file).read()

	cache_fn = script_path + '/cache.json'
	if os.path.exists(cache_fn):
		IMG_CACHE = json.loads(open(cache_fn, 'r').read())
	else:
		for key in IMG_CACHE.keys():
			IMG_CACHE[key] = { 'url': IMG_CACHE[key], }

	kanojo = Kanojo(last_msg_hash)
	kanojo.IS_KEY = IS_KEY;
	kanojo.update_cache = True
	kanojo.IMG_CACHE = IMG_CACHE

	html_data = kanojo.get_htmldata(server)
	#html_data = open('index.html').read()

	if not isinstance(html_data, int):
		msgs = kanojo.parse_activities(html_data)
		print len(msgs)
		if len(msgs):
			fn = '/'.join(script_path.split('/')[:-1])+'/%s.md'%dt.strftime('%Y_%m_%d')
			ex = os.path.isfile(fn)

			f = open(fn, 'a')

			if not ex:
				f.write('![img](http://gdrive-cdn.herokuapp.com/537b65a5bc09f0000721dda7/512px-barcode.png)\n\n')

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

	if random.randrange(15) == 0:
		barrier_time = time() - 60*60*24
		for key in IMG_CACHE.keys():
			if IMG_CACHE[key].has_key('time'):
				if barrier_time > IMG_CACHE[key]['time']: 
					del IMG_CACHE[key]
			else:
				del IMG_CACHE[key]

	cache_str = json.dumps(IMG_CACHE, sort_keys=True, indent=4, separators=(',', ': '))
	f = open(cache_fn, 'w')
	f.write(cache_str.encode('utf-8'))
	f.close()

	if WRITE_LOG:
		log = file('%s/kanojo.log'%script_path, 'a+')
		pid = os.getpid()
		cmd1 = file('/proc/%d/cmdline'%pid).read()
		log.write('%s\t%d\t%s'%(strftime("%Y-%m-%d %H:%M:%S", localtime()), pid, cmd1))
		log.write('\ttime: %.2fsec'%(time()-start_time))
		log.write('\n')
		log.close()
