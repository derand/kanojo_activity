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
SELECTED_USER_ID = getattr(settings, 'SELECTED_USER_ID', {})
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
			s = '\033[1;32m%d\033[00m'%k['ean']
		elif not SELECTED_USER_ID in info.followers_ids:
			s = '\033[1;31m%d\033[00m'%k['ean']
		else:
			s = '%d'%k['ean']
		print '\t%s\t%s\t%s'%(s, info.name, info.steady_name)
	

