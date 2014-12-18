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
KANOJOS_INFO = getattr(settings, 'KANOJOS_INFO', {})
SELECTED_USER_ID = getattr(settings, 'SELECTED_USER_ID', 0)
FRIENDS_USER_IDS = getattr(settings, 'FRIENDS_USER_IDS', [])
from libkanojo import Kanojo, KanojoInfo


if __name__=='__main__':
	kanojo = Kanojo()
	'''
	html_data = open('i.html').read()
	info = kanojo.parse_kanojo(html_data)
	s = ''
	if info.steady_id == SELECTED_USER_ID:
		s = '\033[1;32m%d\033[00m'%11111
	elif not SELECTED_USER_ID in info.followers_ids:
		s = '\033[1;31m%d\033[00m'%11111
	else:
		s = '%d'%11111
	print '\t%s\t%s\t%s'%(s, info.name, info.steady_name)
	'''
	for k in KANOJOS_INFO:
		html_data = kanojo.get_htmldata(k['url'])
		info = kanojo.parse_kanojo(html_data)
		s = ''
		if info.steady_id == SELECTED_USER_ID:
			s = '\033[1;32m%s\033[00m'%k['ean']
		elif info.steady_id in FRIENDS_USER_IDS or (k.has_key('steady') and ((isinstance(k['steady'], int) and k['steady'] == info.steady_id) or (isinstance(k['steady'], list) and info.steady_id in k['steady'])) ):
			#s = '\033[1;36m%d\033[00m'%k['ean']
			s = '%s'%k['ean']
		else:
			s = '\033[1;31m%s\033[00m'%k['ean']
		if info.steady_id == SELECTED_USER_ID or SELECTED_USER_ID in info.followers_ids:
			s += '\033[1;32m [OK]\033[00m'
		else:
			s += '\033[1;31m [nFOUND]\033[00m'
		name_id = '%s(%d)'%(info.name, info.kid)
		print '\t%s\t\033[1;33m%s\033[00m\t%s\t%s'%(s, name_id.ljust(10), info.life, info.steady_name)
