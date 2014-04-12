#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
from StringIO import StringIO
from xml.dom import minidom
import pycurl, os

class UploadToImageshack(object):
	def __init__(self, IS_key):
		super(UploadToImageshack, self).__init__()
		self.key = IS_key

	def parseXML(self, xml):
		try:
			xmldoc = minidom.parse(StringIO(xml))
			rv = xmldoc.getElementsByTagName("image_link")[0].firstChild.data
			#except IndexError:
			#	rv = False
		except:
			rv = False
		return rv

	def upload(self, file_path_or_url):
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, 'https://post.imageshack.us/upload_api.php')
		curl.setopt(pycurl.POST, 1)
		if os.path.isfile(file_path_or_url):
			curl.setopt(pycurl.HTTPPOST, [('fileupload', (pycurl.FORM_FILE, file_path_or_url)), ('format', 'xml'), ('key', self.key)])
		elif 'http' == file_path_or_url[:4]:
			curl.setopt(pycurl.HTTPPOST, [('url', file_path_or_url), ('format', 'xml'), ('key', self.key)])
		buf = StringIO()
		curl.setopt(pycurl.WRITEFUNCTION, buf.write)
		try:
			curl.perform()
		except pycurl.error:
			print 'asd'
			print pycurl.error
			return False
		return self.parseXML(buf.getvalue().strip())

if __name__=='__main__':
	from settings import IS_KEY
	sti = UploadToImageshack(IS_KEY)
	output = sti.upload(argv[1])
	print output
