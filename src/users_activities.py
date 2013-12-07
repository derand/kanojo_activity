#!/usr/bin/env python
# -*- coding: utf-8 -*-


__version__ = '0.01'
__copyright__ = 'Copyright © 2013'


import sys
try:
	settings = __import__('settings')
except ImportError:
	print 'Error import module "settings", see settings.py.template'
	sys.exit(1)
IS_KEY = getattr(settings, 'IS_KEY')
IMG_CACHE = getattr(settings, 'IMG_CACHE', {})
USERS = getattr(settings, 'USERS', [])
import os.path
import datetime, pytz
from libkanojo import ActivityBlock, Kanojo
import json
import os
from time import localtime, strftime

domain='www.barcodekanojo.com'
server='http://%s'%domain


if __name__=='__main__':
	script_path = os.path.dirname(os.path.realpath(__file__))

	log = file('%s/../../kanojo.log'%script_path, 'a+')

	# check if script alredy running
	pid = str(os.getpid())

	cmd1 = file('/proc/%s/cmdline'%pid).read()
	log.write('%s\t%s\t%s'%(strftime("%Y-%m-%d %H:%M:%S", localtime()), pid, cmd1))
	pidfile = "/tmp/kanojo_user_activities.pid"
	if os.path.isfile(pidfile):
		pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
		last_pid = file(pidfile).read()
		if last_pid in pids:
			fn = '/proc/%s/cmdline'%last_pid
			cmd2 = file(fn).read()
			if os.path.isfile(fn) and cmd1==cmd2 and pid<>last_pid:
				print "%s already exists, exiting" % pidfile
				log.write('\t--- parent: %s\t<%s>\n'%(last_pid, cmd2))
				log.close()
				sys.exit()
	log.write('\n')
	log.close()
	
	file(pidfile, 'w').write(pid)

	status_fn = script_path + '/status.json'
	status = {}
	if os.path.exists(status_fn):
		status = json.loads(open(status_fn, 'r').read())

	users_dir = '/'.join(script_path.split('/')[:-1])+'/hidden'
	if not os.path.exists(users_dir):
		os.makedirs(users_dir)

	kanojo = Kanojo()
	kanojo.IS_KEY = IS_KEY;
	kanojo.IMG_CACHE = IMG_CACHE
	for usr in USERS:
		dt = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
		if usr.has_key('username'):
			usr_name = usr['username']
		else:
			usr_name = usr['url'].split('/')[-1]
		print usr_name
		html_data = kanojo.get_htmldata(usr['url'])
		#html_data = open('Lemuel').read()

		if not isinstance(html_data, int):
			usr_dir = users_dir + '/' + usr_name
			if not os.path.exists(usr_dir):
				os.makedirs(usr_dir)
			if not status.has_key(usr['url']):
				status[usr['url']] = {}
			if status[usr['url']].has_key('last_msg_hash'):
				kanojo.last_msg_hash = status[usr['url']]['last_msg_hash']
			else:
				kanojo.last_msg_hash = None
			msgs = kanojo.parse_activities(html_data)
			print len(msgs)
			if len(msgs):
				fn = usr_dir + '/%s_%s.md'%(usr_name, dt.strftime('%Y_%m_%d'))

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

				status[usr['url']]['last_msg_hash'] = msgs[-1].hash()

	status_str = json.dumps(status, sort_keys=True, indent=4, separators=(',', ': '))
	f = open(status_fn, 'w')
	f.write(status_str.encode('utf-8'))
	f.close()

	os.unlink(pidfile)
