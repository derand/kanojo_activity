#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
from StringIO import StringIO
from xml.dom import minidom
import pycurl, os
import json

class UploadToCDN(object):
	def __init__(self, IS_key):
		super(UploadToCDN, self).__init__()
		self.key = IS_key

	def getLink(self, json_str):
		try:
			tmp = json.loads(json_str)
		except ValueError:
			return False
		return tmp.get('url', False)

	def upload(self, file_path_or_url):
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, 'http://gdrive-cdn.herokuapp.com/upload')
		curl.setopt(pycurl.POST, 1)
		if os.path.isfile(file_path_or_url):
			return False
			#curl.setopt(pycurl.HTTPPOST, [('fileupload', (pycurl.FORM_FILE, file_path_or_url)), ('format', 'xml'), ('key', self.key)])
		elif 'http' == file_path_or_url[:4]:
			curl.setopt(pycurl.HTTPPOST, [('url', file_path_or_url), ('key', self.key)])
		buf = StringIO()
		curl.setopt(pycurl.WRITEFUNCTION, buf.write)
		try:
			curl.perform()
		except pycurl.error:
			return False
		return self.getLink(buf.getvalue().strip())

if __name__=='__main__':
	from settings import IS_KEY
	sti = UploadToCDN(IS_KEY)
	output = sti.upload(argv[1])
	print output
