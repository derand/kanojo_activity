#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.01'
__copyright__ = 'Copyright © 2013'

import lxml.html
import urllib
import hashlib
import os.path
import datetime, pytz
import re
from imageshack import UploadToImageshack
from settings import IS_KEY

domain='www.barcodekanojo.com'
server='http://%s'%domain

def get_url(data, isImage=False):
	if data.find(domain) == -1:
		data = server+data
	if not isImage:
		return data
	sti = UploadToImageshack(IS_KEY)
	url = sti.upload(data)
	if url == False:
		url = data
	return url

def html2markdown(tag):
	# [Lemuel](http://www.barcodekanojo.com/user/399321/Lemuel) added [Junko](http://www.barcodekanojo.com/kanojo/2541211/Junko) to friend list.
	# <a href="/user/399321/Lemuel">Lemuel</a> added <a href="/kanojo/2541211/Junko">Junko</a> to friend list.
	for a in tag.xpath('.//a'):
		url = ''
		for attr in a.items():
			if 'href' == attr[0]:
				url = get_url(attr[1])
				break
		tmp = '[%s](%s)'%(a.text, url)
		a.tail = tmp + a.tail if a.tail else tmp
	lxml.etree.strip_elements(tag, 'a', with_tail=False)
	s = lxml.etree.tostring(tag, encoding='utf-8', method='html').strip()
	s = s[s.index('>')+1:s.rindex('<')]
	return s

def get_data(url):
	page = urllib.urlopen(url)
	code = page.getcode()
	if code == 200:
		return page.read()
	return code

class ActivityBlock(object):
	"""docstring for ActivityBlock"""
	def __init__(self, div_tag=None):
		super(ActivityBlock, self).__init__()
		self.l_box_image = None
		self.l_box_url = None
		self.r_box_image = None
		self.r_box_url = None
		self.c_box_text = None
		self.time = None
		if div_tag != None:
			self.parse(div_tag)

	def hash(self):
		m = hashlib.md5()
		m.update(self.c_box_text)
		return m.hexdigest()

	def parse(self, div_tag):
		for el in div_tag.iterchildren():
			if 'div' == el.tag and len(el.find_class('l_activities_box')) and el.find_class('l_activities_box')[0] == el:
				for el2 in el.iterchildren():
					if 'a' == el2.tag:
						for attr in el2.items():
							if 'href' == attr[0]:
								self.l_box_url = get_url(attr[1])
						for el3 in el2.iterchildren():
							if 'img' == el3.tag:
								for attr in el3.items():
									if 'src' == attr[0]:
										self.l_box_image = get_url(attr[1], True)
										break
								break
						break
			if 'div' == el.tag and len(el.find_class('r_activities_box')) and el.find_class('r_activities_box')[0] == el:
				for el2 in el.iterchildren():
					if 'a' == el2.tag:
						for attr in el2.items():
							if 'href' == attr[0]:
								self.r_box_url = get_url(attr[1])
						for el3 in el2.iterchildren():
							if 'img' == el3.tag:
								for attr in el3.items():
									if 'src' == attr[0]:
										self.r_box_image = get_url(attr[1], True)
										break
								break
						break
					if 'img' == el3.tag:
						for attr in el3.items():
							if 'src' == attr[0]:
								self.r_box_image = get_url(attr[1], True)
								self.r_box_url = get_url(attr[1], False)
								break
						break
			if 'div' == el.tag and len(el.find_class('c_activities_box')) and el.find_class('c_activities_box')[0] == el:
				r = re.compile('@[\D*](\d+)\s+(\w+)\s+ago')
				for el2 in el.iterchildren():
					if 'span' == el2.tag:
						for attr in el2.items():
							if 'id' == attr[0] and 'activity.message' == attr[1]:
								self.c_box_text = html2markdown(el2)
								break
						m = r.search(el2.text.strip())
						if m:
							g = m.groups()
							self.time = int(g[0])
							if g[1][0] == 'm': self.time *= 60
							if g[1][0] == 'h': self.time *= 60*60


class Kanojo(object):
	"""docstring for Kanojo"""
	def __init__(self, last_id=None):
		super(Kanojo, self).__init__()
		self.doc = None
		self.last_id = last_id

	def parse_data(self, html_data):
		self.doc = lxml.html.document_fromstring(html_data)
		start_activity_block = self.doc.get_element_by_id('activityBlock', None)
		activities = []
		for el in start_activity_block.iterchildren():
			if 'div' == el.tag and el.find_class('activities_box')[0] == el:
				ab = ActivityBlock(el)
				if ab.hash() == self.last_id:
					break
				activities.append(ab)
		activities.reverse()
		return activities


if __name__=='__main__':
	script_path = os.path.dirname(os.path.realpath(__file__))

	html_data = get_data(server)
	#html_data = open('index.html').read()

	dt = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
	last_msg_hash = None
	hash_file = script_path+'/last_msg_hash'
	if os.path.isfile(hash_file):
		last_msg_hash = open(hash_file).read()
	if not isinstance(html_data, int):
		kanojo = Kanojo(last_msg_hash)
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
					#str += ' <div style="float: right">[![img](%s)](%s)</div>'%(ab.r_box_image, ab.r_box_url)
				f.write('\n\n')
			f.close()

			f = open(hash_file, 'w')
			f.write(msgs[-1].hash())
			f.close()
