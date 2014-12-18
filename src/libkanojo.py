#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.04'
__copyright__ = 'Copyright © 2013'

import sys
import lxml.html
import urllib
import hashlib
import os.path
import datetime, pytz
import re
import time
from imageshack import UploadToImageshack
from gdrive_cdn import UploadToCDN
from deviantsart_cdn import UploadToDeviantsart


class ActivityBlock(object):
	"""docstring for ActivityBlock"""
	def __init__(self, div_tag=None, IS_KEY='', IMG_CACHE={}, domain='', update_cache=False):
		super(ActivityBlock, self).__init__()
		self.l_box_image = None
		self.l_box_url = None
		self.r_box_image = None
		self.r_box_url = None
		self.c_box_text = None
		self.time = None
		self.IS_KEY = IS_KEY
		self.IMG_CACHE = IMG_CACHE
		self.domain = domain
		self.update_cache = update_cache
		if div_tag != None:
			self.parse(div_tag)

	def hash(self):
		m = hashlib.md5()
		m.update(self.c_box_text)
		return m.hexdigest()

	def __prepare_url(self, data, isImage=False):
		'''
			http://www.barcodekanojo.com/profile_images/kanojo/2890681/1397673056/50x50xHors.png,qw=88,ah=88,aface=true.pagespeed.ic.WxA3iTfrxh.png
			http://www.barcodekanojo.com/profile_images/user/445543/1396835017/50x50xAntuaneten.jpg,qw=88,ah=88.pagespeed.ic.OUxW8WYlsH.jpg
			http://www.barcodekanojo.com/profile_images/user/445543/1396835017/Antuaneten.jpg?w=88&h=88
		'''
		if data.find(self.domain) == -1:
			data = 'http://%s'%self.domain+data
		#return data
		if isImage:
			idx = data.find(',')
			if idx > 0 and data.find('/50x50x') > 0:
				ext = '.'+data.split('.')[-1]
				data_tmp = data[:idx].replace('/50x50x', '/')
				if data_tmp[-1] == '/':
					name = data[idx:].split('.')
					if len(name) > 2:
						data_tmp += name[-2] + '.' + name[-1]
				add = '?w=88&h=88'
				if data.find('aface=true') > 0:
					add += '&face=true'
				if data_tmp[-len(ext):] != ext:
					add = ext + add
				#with open('/home/pi/share/translate.log', 'a') as myfile:
				#	myfile.write(data + ' --> ' + (data_tmp + add) + '\n')
				data = data_tmp + add
		return data

	def __copy_img(self, src_url):
		usr_id = None
		r = re.compile('profile_images\/user\/(\d+)\/')
		m = r.search(src_url)
		if m:
			g = m.groups()
			usr_id = g[0]
		if usr_id and self.IMG_CACHE.has_key(usr_id):
			if isinstance(self.IMG_CACHE[usr_id], dict):
				if self.update_cache:
					if self.IMG_CACHE[usr_id].has_key('counter'):
						self.IMG_CACHE[usr_id]['counter'] = self.IMG_CACHE[usr_id]['counter']+1
					else:
						self.IMG_CACHE[usr_id]['counter'] = 1
					self.IMG_CACHE[usr_id]['time'] = time.time()
				if self.IMG_CACHE[usr_id].has_key('url'):
					return self.IMG_CACHE[usr_id]['url']
			else:
				return self.IMG_CACHE[usr_id]
		#sti = UploadToImageshack(self.IS_KEY)
		#sti = UploadToCDN()
		sti = UploadToDeviantsart()
		url = sti.upload(src_url)
		if url:
			if usr_id and self.update_cache and not self.IMG_CACHE.has_key(usr_id):
				self.IMG_CACHE[usr_id] = {
					'url': url,
					'counter': 0,
					'time': time.time()
				}
		else:
			# if can't upload try another cdn
			url = UploadToCDN().upload(src_url)
			if url == False:
				url = 'http://i.imgur.com/WR0naKP.jpg'
		#if '23q3t7f' in url:
		#	with open('/home/pi/share/error.log', 'a') as myfile:
		#		myfile.write(src_url+'\n')
		return url

	def copy_imgs(self):
		if self.l_box_image:
			self.l_box_image = self.__copy_img(self.l_box_image)
		if self.r_box_image:
			self.r_box_image = self.__copy_img(self.r_box_image)

	def html2markdown(self, tag):
		# [Lemuel](http://www.barcodekanojo.com/user/399321/Lemuel) added [Junko](http://www.barcodekanojo.com/kanojo/2541211/Junko) to friend list.
		# <a href="/user/399321/Lemuel">Lemuel</a> added <a href="/kanojo/2541211/Junko">Junko</a> to friend list.
		for a in tag.xpath('.//a'):
			url = ''
			for attr in a.items():
				if 'href' == attr[0]:
					url = self.__prepare_url(attr[1], False)
					break
			tmp = '[%s](%s)'%(a.text, url)
			a.tail = tmp + a.tail if a.tail else tmp
		lxml.etree.strip_elements(tag, 'a', with_tail=False)
		s = lxml.etree.tostring(tag, encoding='utf-8', method='html').strip()
		s = s[s.index('>')+1:s.rindex('<')]
		return s

	def parse(self, div_tag):
		for el in div_tag.iterchildren():
			if 'div' == el.tag and len(el.find_class('l_activities_box')) and el.find_class('l_activities_box')[0] == el:
				for el2 in el.iterchildren():
					if 'a' == el2.tag:
						for attr in el2.items():
							if 'href' == attr[0]:
								self.l_box_url = self.__prepare_url(attr[1], False)
						for el3 in el2.iterchildren():
							if 'img' == el3.tag:
								for attr in el3.items():
									if 'src' == attr[0]:
										self.l_box_image = self.__prepare_url(attr[1], True)
										break
								break
						break
			if 'div' == el.tag and len(el.find_class('r_activities_box')) and el.find_class('r_activities_box')[0] == el:
				for el2 in el.iterchildren():
					if 'a' == el2.tag:
						for attr in el2.items():
							if 'href' == attr[0]:
								self.r_box_url = self.__prepare_url(attr[1], False)
						for el3 in el2.iterchildren():
							if 'img' == el3.tag:
								for attr in el3.items():
									if 'src' == attr[0]:
										self.r_box_image = self.__prepare_url(attr[1], True)
										break
								break
						break
					if 'img' == el2.tag:
						for attr in el2.items():
							if 'src' == attr[0]:
								self.r_box_image = self.__prepare_url(attr[1], True)
								self.r_box_url = self.__prepare_url(attr[1].split('?')[0], False)
								break
						break
			if 'div' == el.tag and len(el.find_class('c_activities_box')) and el.find_class('c_activities_box')[0] == el:
				r = re.compile('@[\D*](\d+)\s+(\w+)\s+ago')
				for el2 in el.iterchildren():
					if 'span' == el2.tag:
						for attr in el2.items():
							if 'id' == attr[0] and 'activity.message' == attr[1]:
								self.c_box_text = self.html2markdown(el2)
								break
						m = r.search(el2.text.strip())
						if m:
							g = m.groups()
							self.time = int(g[0])
							if g[1][0:2] == 'mi': self.time *= 60
							if g[1][0]   == 'h': self.time *= 60*60
							if g[1][0]   == 'd': self.time *= 24*60*60
							if g[1][0]   == 'w': self.time *= 7*24*60*60
							if g[1][0:2] == 'mo': self.time *= 30*24*60*60

class KanojoInfo(object):
	"""docstring for KanojoInfo"""
	def __init__(self):
		super(KanojoInfo, self).__init__()
		self.name = None
		self.steady_name = ''
		self.steady_id = None
		self.followers_ids = []
		self.life = '-1%'


class Kanojo(object):
	"""docstring for Kanojo"""
	def __init__(self, last_msg_hash=None):
		super(Kanojo, self).__init__()
		self.doc = None
		self.last_msg_hash = last_msg_hash
		self.IS_KEY = None
		self.IMG_CACHE = None
		self.update_cache = False
		self.domain = 'www.barcodekanojo.com'

	def parse_activities(self, html_data):
		self.doc = lxml.html.document_fromstring(html_data)
		start_activity_block = self.doc.get_element_by_id('activityBlock', None)
		activities = []
		for el in start_activity_block.iterchildren():
			if 'div' == el.tag and el.find_class('activities_box')[0] == el:
				ab = ActivityBlock(el, IS_KEY=self.IS_KEY, IMG_CACHE=self.IMG_CACHE, domain=self.domain, update_cache=self.update_cache)
				if ab.hash() == self.last_msg_hash:
					break
				ab.copy_imgs()
				activities.append(ab)
		activities.reverse()
		return activities

	def get_htmldata(self, url):
		page = urllib.urlopen(url)
		code = page.getcode()
		if code == 200:
			return page.read()
		return code

	def parse_kanojo(self, html_data):
		rv = KanojoInfo()
		kanojo_doc = lxml.html.document_fromstring(html_data)
		main_content_block = kanojo_doc.get_element_by_id('maincontent', None)
		if main_content_block != None:
			for el in main_content_block.xpath('./h1'):
				for attr in el.items():
					if 'class' == attr[0] and 'name_kanojo' == attr[1]:
						rv.name = el.text
						break
			profile_img = main_content_block.xpath('./table/tr/td/div/img')
			if len(profile_img):
				profile_img = profile_img[0].get('src')
				rv.kid = int(profile_img.split('/')[5])
			#//*[@id="maincontent"]/table/tbody/tr/td[2]/table/tbody/tr[4]/td[2]/div/a
			#//*[@id="maincontent"]/table/tbody/tr/td[2]/table/tbody/tr[5]/td[2]/div/img
			tbl = main_content_block.xpath('./table/tr/td/table')
			if len(tbl)>0:
				tbl = tbl[0]
				tmp = tbl.xpath('./tr[4]/td[2]/div/a')
				if len(tmp):
					usr = tmp[0].get('href').split('/')
					rv.steady_id = int(usr[2])
					rv.steady_name = '/'.join(usr[3:])
				tmp = tbl.xpath('./tr[5]/div/td/div/img')
				if len(tmp):
					rv.life = tbl.xpath('./tr[5]/div/td/div/img')[0].get('width')
			# followers
			for el in main_content_block.iterchildren():
				if 'span' == el.tag:
					tmp = el.xpath('./span/a')
					if len(tmp):
						usr = tmp[0].get('href')
						rv.followers_ids.append(int(usr.split('/')[2]))
		return rv



# download all activities
if __name__=='__main__':
	try:
		settings = __import__('settings')
	except ImportError:
		print 'Error import module "settings", see settings.py.template'
		sys.exit(1)
	IS_KEY = getattr(settings, 'IS_KEY')
	IMG_CACHE = getattr(settings, 'IMG_CACHE', {})

	script_path = os.path.dirname(os.path.realpath(__file__))

	dt = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
	last_msg_hash = None
	hash_file = script_path+'/last_msg_hash'
	if os.path.isfile(hash_file):
		last_msg_hash = open(hash_file).read()

	kanojo = Kanojo(last_msg_hash)
	kanojo.IS_KEY = IS_KEY;
	kanojo.IMG_CACHE = IMG_CACHE
	html_data = kanojo.get_htmldata('http://%s'%kanojo.domain)
	#html_data = open('index.html').read()

	if not isinstance(html_data, int):
		msgs = kanojo.parse_activities(html_data)
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
