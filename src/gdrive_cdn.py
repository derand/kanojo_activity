#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
from StringIO import StringIO
import pycurl, os
import json

class UploadToCDN(object):
	def __init__(self):
		super(UploadToCDN, self).__init__()

	def getLink(self, json_str):
		try:
			print json_str
			tmp = json.loads(json_str)
		except ValueError:
			return False
		return tmp.get('url', False)

	def upload(self, file_path_or_url):
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, 'http://gdrive-cdn.herokuapp.com/upload')
		#curl.setopt(pycurl.URL, 'http://cdn.derand.net/upload')
		#curl.setopt(pycurl.URL, 'http://localhost:5000/upload')
		curl.setopt(pycurl.POST, 1)
		if os.path.isfile(file_path_or_url):
			curl.setopt(pycurl.HTTPPOST, [('file', (pycurl.FORM_FILE, file_path_or_url))])
		elif 'http' == file_path_or_url[:4]:
			#curl.setopt(pycurl.HTTPPOST, [('url', file_path_or_url), ('key', self.key)])
			curl.setopt(pycurl.HTTPPOST, [('url', file_path_or_url)])
		buf = StringIO()
		curl.setopt(pycurl.WRITEFUNCTION, buf.write)
		try:
			curl.perform()
		except pycurl.error as e:
			print e
			return False
		return self.getLink(buf.getvalue().strip())

if __name__=='__main__':
	sti = UploadToCDN()
	output = sti.upload(argv[1])
	print output
